from typing import Optional

import sqlalchemy
from fastapi import Request
from pydantic import BaseModel, Field

from .api_model.response_model import ApiResponse



def check_user(uid: str, engine):
    conn = engine.connect()

    result = conn.execute(sqlalchemy.text("""
                    SELECT uid, username, email
                    FROM user_info
                    WHERE uid = :uid
                """), {
            "uid": uid
    })
    conn.commit()
    userinfo = result.fetchone()
    return userinfo


async def get_user_info(uid: str, engine):
    conn = engine.connect()
    try:
        userinfo = check_user(uid, engine)
        if userinfo is None:
            return ApiResponse(code=404, msg="用户信息未找到")

        response = ApiResponse(code=200,
                               data={
                               },
                               msg="查询成功")

        result = conn.execute(sqlalchemy.text("""
                            SELECT uid, stu_num, major, stu_position, class_name
                            FROM stu_detail
                            WHERE uid = :uid
                        """), {
            "uid": uid
        })
        conn.commit()
        stu_info = result.fetchone()
        if stu_info:
            response.data = {
                "uid": userinfo[0],
                "username": userinfo[1],
                "email": userinfo[2],
                "stu_info": {
                    "stu_num": stu_info[1],
                    "major": stu_info[2],
                    "stu_position": stu_info[3],
                    "class_name": stu_info[4],
                }
            }
            return response

        result = conn.execute(sqlalchemy.text("""
                            SELECT uid, teacher_num
                            FROM teacher_detail
                            WHERE uid = :uid
                        """), {
            "uid": uid
        })
        conn.commit()
        teacher_info = result.fetchone()
        if teacher_info:
            response.data = {
                                   "uid": userinfo[0],
                                   "username": userinfo[1],
                                   "email": userinfo[2],
                                   "teacher_info": {
                                       "teacher_num": teacher_info[1],
                                   }
                               }
            return response

        response.data={
                               "uid": userinfo[0],
                               "username": userinfo[1],
                               "email": userinfo[2],
                           }
        return response

    except Exception as e:
        print(e)
        return ApiResponse(code=500, msg="查询用户信息发生错误")
    finally:
        conn.close()


async def get_user_info_api(request: Request, uid: str, engine):
    # print(request.state.user)
    token_uid = request.state.user.get("uid")
    if not token_uid or token_uid != uid:
        ApiResponse(code=400, msg=f'{token_uid} 无权限查看 {uid} ')
        print(token_uid)
    response = await get_user_info(uid, engine)
    return response



