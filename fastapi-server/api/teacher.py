from typing import Optional

import sqlalchemy
from fastapi import Request
from pydantic import BaseModel, Field

from .api_model.response_model import ApiResponse


def check_user_is_teacher(uid: str, engine):
    conn = engine.connect()
    result = conn.execute(sqlalchemy.text("""
                    SELECT *
                    FROM teacher_detail
                    WHERE uid = :uid
                """), {
            "uid": uid
    })
    conn.commit()
    teacher_info = result.fetchone()
    return teacher_info


async def get_teacher_class(uid: str, engine):
    conn = engine.connect()
    result = conn.execute(sqlalchemy.text("""
                    SELECT class_name
                    FROM class
                    WHERE class.teacher_uid = :uid
                """), {
            "uid": uid
    })
    class_list = result.fetchall()
    response = ApiResponse(code=200,
                           data={
                               "class_list": [item[0] for item in class_list]
                           },
                           msg="查询成功")
    return response


async def get_teacher_class_api(request: Request, uid: str, engine):
    # print(request.state.user)
    token_uid = request.state.user.get("uid")

    if not token_uid or token_uid != uid:
        print(token_uid)
        return ApiResponse(code=400, msg=f'{token_uid} 无权限查看 {uid} ')

    teacher_auth = check_user_is_teacher(uid, engine)
    if not teacher_auth:
        print(teacher_auth)
        return ApiResponse(code=400, msg=f'{token_uid} 无教师权限')

    response = await get_teacher_class(uid, engine)
    return response
