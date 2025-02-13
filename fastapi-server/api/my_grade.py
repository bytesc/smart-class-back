import sqlalchemy
from fastapi import Request
from pydantic import BaseModel, Field

from .api_model.response_model import ApiResponse
from .user import check_user


async def get_my_grade_list(uid: str, engine):
    conn = engine.connect()
    try:
        response = ApiResponse(code=200,
                               data={
                               },
                               msg="查询成功")

        stu_grade_result = conn.execute(sqlalchemy.text("""
                                SELECT stu_detail.uid, stu_detail.stu_num, user_info.username,
                                 stu_grade.grade, stu_grade.semester,
                                 lesson_info.lesson_num, lesson_info.lesson_name
                                FROM stu_grade, stu_detail, user_info, lesson_info
                                WHERE stu_detail.uid = :uid and stu_grade.uid = :uid and user_info.uid = :uid
                                and lesson_info.lesson_num = stu_grade.lesson_num
                            """), {
            "uid": uid
        })
        conn.commit()
        stu_grade_list = stu_grade_result.fetchall()
        print(stu_grade_result)
        if stu_grade_list:
            response.data = {
                "stu_grade_list": [
                    {
                        "grade": grade[3],
                        "semester": grade[4],
                        "lesson_num": grade[5],
                        "lesson_name": grade[6],
                    } for grade in stu_grade_list
                ]
            }
        return response

    except Exception as e:
        print(e)
        return ApiResponse(code=500, msg="查询成绩列表信息发生错误")
    finally:
        conn.close()


from .teacher import check_user_is_teacher
async def get_my_grade_list_api(request: Request, uid: str, engine):
    # print(request.state.user)
    token_uid = request.state.user.get("uid")
    teacher = check_user_is_teacher(token_uid, engine)
    if not token_uid or (token_uid != uid and not teacher):
        ApiResponse(code=400, msg=f'{token_uid} 无权限查看 {uid} ')
        print(token_uid)
    response = await get_my_grade_list(uid, engine)
    return response



async def get_class_grade_list(class_name: str, engine):
    conn = engine.connect()
    try:
        response = ApiResponse(code=200,
                               data={
                               },
                               msg="查询成功")

        class_grade_result = conn.execute(sqlalchemy.text("""
                                SELECT stu_detail.uid, stu_detail.stu_num, user_info.username,
                                 ROUND(AVG(stu_grade.grade), 3)
                                FROM stu_grade
                                JOIN stu_detail ON stu_grade.uid = stu_detail.uid
                                JOIN user_info ON stu_grade.uid = user_info.uid
                                JOIN lesson_info ON lesson_info.lesson_num = stu_grade.lesson_num
                                WHERE stu_detail.class_name = :class_name and stu_grade.grade IS NOT NULL
                                GROUP BY user_info.uid
                            """), {
            "class_name": class_name
        })
        conn.commit()
        class_grade_list = class_grade_result.fetchall()
        print(class_grade_result)
        if class_grade_list:
            response.data = {
                "class_grade_list": [
                    {
                        "uid": grade[0],
                        "stu_num": grade[1],
                        "username": grade[2],
                        "avg_grade": grade[3],
                    } for grade in class_grade_list
                ]
            }
        return response

    except Exception as e:
        print(e)
        return ApiResponse(code=500, msg="查询成绩列表信息发生错误")
    finally:
        conn.close()


from .teacher import check_user_is_teacher
async def get_class_grade_list_api(request: Request, class_name: str, engine):
    # print(request.state.user)
    token_uid = request.state.user.get("uid")
    teacher = check_user_is_teacher(token_uid, engine)
    if not token_uid or not teacher:
        ApiResponse(code=400, msg=f'{token_uid} 无权限查看 {class_name} ')
        print(token_uid)
    response = await get_class_grade_list(class_name, engine)
    return response
