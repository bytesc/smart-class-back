import jwt
import sqlalchemy
from fastapi import Request
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta
from .api_model.response_model import ApiResponse
from .utils.rsa.keys import PRIVATE_KEY
from .utils.rsa.token import create_access_token


class UserRegisterModel(BaseModel):
    uid: str = Field(..., min_length=3, max_length=50, description="手机号")
    username: str = Field(..., min_length=1, max_length=50, description="姓名")
    email: Optional[str] = Field(default="", max_length=200, description="邮箱")
    password: str = Field(..., min_length=6, max_length=50, description="密码")


async def registerApi(request: Request, data: UserRegisterModel, engine):
    conn = engine.connect()
    result_auth = conn.execute(sqlalchemy.text("SELECT * FROM user_auth WHERE uid = :uid"),
                               {"uid": data.uid})
    result_info = conn.execute(sqlalchemy.text("SELECT * FROM user_info WHERE uid = :uid"),
                               {"uid": data.uid})
    conn.commit()
    if result_info.fetchone() is not None or result_auth.fetchone() is not None:
        return ApiResponse(code=400, msg="手机号已存在")

    try:
        with conn.begin():
            conn.execute(sqlalchemy.text("""
                INSERT INTO user_info (uid, username, email)
                VALUES (:uid, :username, :email);
            """), {
                "uid": data.uid,
                "username": data.username,
                "email": data.email
            })
    except Exception as e:
        conn.rollback()
        print(e)
        return ApiResponse(code=500, msg="创建失败")
    try:
        with conn.begin():
            conn.execute(sqlalchemy.text("""
                INSERT INTO user_auth (uid, password, retry_count, login_time)
                VALUES (:uid, :password, :retry_count, :login_time);
            """), {
                "uid": data.uid,
                "password": data.password,
                "retry_count": 0,
                "login_time": datetime.utcnow(),
            })
    except Exception as e:
        conn.rollback()
        print(e)
        return ApiResponse(code=500, msg="创建失败")
    finally:
        conn.close()
    return ApiResponse(code=200, msg="注册成功")


class UserLoginModel(BaseModel):
    uid: str = Field(..., min_length=3, max_length=50, description="手机号")
    password: str = Field(..., min_length=6, description="密码")


async def loginApi(request: Request, data: UserLoginModel, engine):
    conn = engine.connect()
    try:
        result_auth = conn.execute(sqlalchemy.text("SELECT * FROM user_auth WHERE uid = :uid"),
                                   {"uid": data.uid})
        result_info = conn.execute(sqlalchemy.text("SELECT * FROM user_info WHERE uid = :uid"),
                                   {"uid": data.uid})
        conn.commit()
        user_auth = result_auth.fetchone()
        user_info = result_info.fetchone()
        if user_auth is None or user_info is None:
            return ApiResponse(code=404, msg="用户不存在")

        # print(user_auth, user_info)
        login_time = user_auth[3]  # login_time
        if login_time > datetime.utcnow():
            time_diff = login_time - datetime.utcnow()
            minutes_diff = int(time_diff.total_seconds() / 60)
            return ApiResponse(code=400, msg=f"请于{minutes_diff}分钟后重试")

        stored_password = user_auth[2]  # password
        if stored_password != data.password:
            if user_auth[4] >= 3:  # retry_count
                login_time = datetime.utcnow() + timedelta(minutes=10)
                conn.execute(sqlalchemy.text("""
                        UPDATE user_auth SET retry_count = 0, login_time = :login_time WHERE uid = :uid
                    """), {
                    "login_time": login_time,
                    "uid": data.uid
                })
            else:
                conn.execute(sqlalchemy.text("""
                        UPDATE user_auth SET retry_count = :retry_count WHERE uid = :uid
                    """), {
                    "retry_count": user_auth[4] + 1,  # retry_count
                    "uid": data.uid
                })
            conn.commit()
            return ApiResponse(code=400, msg="密码错误")

        token = create_access_token(token_payload={"uid": data.uid},
                                    expiration_delta=timedelta(hours=24))
        return ApiResponse(code=200,
                           data={
                               "token": token,
                               "uid": user_info[0],  # uid
                               "username": user_info[1],  # username
                               "email": user_info[3],  # email,
                           },
                           msg="登录成功")
    except Exception as e:
        print(e)
        return ApiResponse(code=500, msg="登录错误")
    finally:
        conn.close()
