import sqlalchemy
from fastapi import Request
from pydantic import BaseModel, Field

from .api_model.response_model import ApiResponse
from .prediction_tools.grade_prediction import predict_for_class, generate_training_dataset


class ClassGradePredictionModel(BaseModel):
    class_name: str = Field(..., min_length=1, max_length=255, description="班级名称")
    lesson_id: str = Field(..., min_length=1, max_length=255, description="课程id")


async def class_grade_prediction_api(request: Request, data: ClassGradePredictionModel, engine):
    conn = engine.connect()
    try:
        predict_result = predict_for_class(data.class_name, data.lesson_id, engine)
        if predict_result is None:
            ApiResponse(code=200,
                        data={
                            "class_name": data.class_name,
                            "lesson_id": data.lesson_id,
                            "result": [],
                        },
                        msg="预测失败，所有学生都缺乏前置成绩")

        result_list = [{"uid": k, "predicted_grade": v} for k, v in predict_result.items()]

        stu_list_result = conn.execute(sqlalchemy.text("""
                            SELECT stu_detail.uid, stu_detail.stu_num, stu_detail.major,
                             stu_detail.stu_position, user_info.username
                            FROM stu_detail, user_info
                            WHERE stu_detail.class_name = :class_name and stu_detail.uid = user_info.uid
                        """), {
            "class_name": data.class_name
        })
        conn.commit()
        stu_list = stu_list_result.fetchall()
        stu_info_dict = {stu[0]: {"stu_num": stu[1], "username": stu[4]} for stu in stu_list}

        result_list_with_info_list = []
        for uid, predicted_grade in predict_result.items():
            stu_info = stu_info_dict.get(uid, {})
            result_list_with_info_list.append({
                "uid": uid,
                "predicted_grade": f"{predicted_grade:.2f}",
                "stu_num": stu_info.get("stu_num"),
                "username": stu_info.get("username")
            })

        return ApiResponse(code=200,
                           data={
                               "class_name": data.class_name,
                               "lesson_id": data.lesson_id,
                               "result": result_list_with_info_list,
                           },
                           msg="预测成功")

    except ValueError as e:
        print(e, type(e))
        return ApiResponse(code=405, msg="没有足够成绩数据作为预测样本")
    except Exception as e:
        print(e, type(e))
        # raise e
        return ApiResponse(code=500, msg=f'预测错误: {str(e)}')
    finally:
        conn.close()


async def check_predictable_lessons_api(request: Request, engine):
    conn = engine.connect()

    try:
        lesson_list_result = conn.execute(sqlalchemy.text("""
                                SELECT lesson_num,lesson_name
                                FROM lesson_info
                            """), {
            "uid": ""
        })
        conn.commit()
        lesson_list = lesson_list_result.fetchall()
        result_list = []
        for lesson in lesson_list:
            lesson_id, lesson_name = lesson
            X, y = generate_training_dataset(lesson_id, engine)
            if len(X) >= 3:
                result_list.append({
                    "lesson_id": lesson_id,
                    "lesson_name": lesson_name,
                    "dataset_length": len(X)
                })

        return ApiResponse(code=200,
                           data={
                               "dataset_length_list": result_list
                           },
                           msg="检查成功")
    except Exception as e:
        print(e, type(e))
        # raise e
        return ApiResponse(code=500, msg=f'数据集检查错误')
    finally:
        conn.close()
