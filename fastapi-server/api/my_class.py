import sqlalchemy
from fastapi import Request
from pydantic import BaseModel, Field

from .api_model.response_model import ApiResponse
from .user import check_user


def check_class(class_name: str, engine):
    conn = engine.connect()
    result = conn.execute(sqlalchemy.text("""
                    SELECT class_name, teacher_uid
                    FROM class
                    WHERE class_name = :class_name
                """), {
        "class_name": class_name
    })
    conn.commit()
    class_info = result.fetchone()
    return class_info


def check_stu_in_class(uid: str,class_name: str, engine):
    conn = engine.connect()
    result = conn.execute(sqlalchemy.text("""
                    SELECT *
                    FROM stu_detail
                    WHERE class_name = :class_name and uid = :uid
                """), {
        "class_name": class_name,
        "uid": uid
    })
    conn.commit()
    stu_in_class = result.fetchone()
    return stu_in_class


async def get_class_list(class_name: str, engine):
    conn = engine.connect()
    try:
        class_info = check_class(class_name, engine)
        if class_info is None:
            return ApiResponse(code=404, msg="班级信息未找到")

        response = ApiResponse(code=200,
                               data={
                               },
                               msg="查询成功")

        stu_list_result = conn.execute(sqlalchemy.text("""
                            SELECT stu_detail.uid, stu_detail.stu_num, stu_detail.major,
                             stu_detail.stu_position, user_info.username
                            FROM stu_detail, user_info
                            WHERE stu_detail.class_name = :class_name and stu_detail.uid = user_info.uid
                        """), {
            "class_name": class_name
        })
        conn.commit()
        stu_list = stu_list_result.fetchall()
        # print(stu_list, class_name)

        teacher_result = conn.execute(sqlalchemy.text("""
                            SELECT user_info.uid, user_info.username, teacher_detail.teacher_num
                            FROM teacher_detail, user_info
                            WHERE user_info.uid = :teacher_uid and user_info.uid = teacher_detail.uid
                        """), {
            "teacher_uid": class_info[1]
        })
        conn.commit()
        class_teacher = teacher_result.fetchone()
        if stu_list:
            response.data = {
                "class_name": class_name,
                "class_teacher_uid": class_teacher[0],
                "class_teacher_name": class_teacher[1],
                "class_teacher_num": class_teacher[2],
                "stu_list": [
                    {
                        "uid": student[0],
                        "stu_num": student[1],
                        "stu_position": student[3],
                        "username": student[4]
                    } for student in stu_list
                ]
            }
        return response

    except Exception as e:
        print(e)
        return ApiResponse(code=500, msg="查询班级列表信息发生错误")
    finally:
        conn.close()


from .teacher import check_user_is_teacher
async def get_class_list_api(request: Request, class_name: str, engine):
    # print(request.state.user)
    token_uid = request.state.user.get("uid")
    print(token_uid,class_name)
    checked_class = check_stu_in_class(token_uid,class_name,engine)
    teacher_auth = check_user_is_teacher(token_uid, engine)
    print(checked_class)
    if not token_uid or (not checked_class and not teacher_auth):
        print(token_uid)
        return ApiResponse(code=400, msg=f'{token_uid} 无权限查看 {class_name} ')
    response = await get_class_list(class_name, engine)
    return response
