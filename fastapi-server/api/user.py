import sqlalchemy
from fastapi import Request
from .api_model.response_model import ApiResponse


async def userInfoApi(request: Request, uid: int, engine):
    print(request.state.user)
    conn = engine.connect()
    try:
        result = conn.execute(sqlalchemy.text("""
                SELECT uid, username, email
                FROM user_info
                WHERE uid = :uid
            """), {
            "uid": uid
        })
        conn.commit()
        userinfo = result.fetchone()
        if userinfo is None:
            return ApiResponse(code=404, msg="用户信息未找到")
        return ApiResponse(code=200,
                           data={
                               "uid": userinfo[0],
                               "username": userinfo[1],
                               "email": userinfo[2],
                           },
                           msg="查询成功")
    except Exception as e:
        print(e)
        return ApiResponse(code=500, msg="查询用户信息发生错误")
    finally:
        conn.close()
