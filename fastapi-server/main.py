import json

import sqlalchemy
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Any
import uvicorn
from starlette.responses import JSONResponse
from utils.get_config import config_data

import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from datetime import datetime, timedelta
import os
from typing import Callable


with open("./rsa/private_key.pem", "rb") as key_file:
    PRIVATE_KEY = key_file.read()
with open("./rsa/public_key.pem", "rb") as key_file:
    PUBLIC_KEY = key_file.read()

# 定义统一的响应模型
class ApiResponse(BaseModel):
    code: int = Field(default=200, description="状态码")
    data: dict = Field(default={}, description="数据内容")
    msg: str = Field(default="成功", description="消息")


class ApiRequest(BaseModel):
    token: str = Field(default=None, description="Token")
    payload: Any


async def auth_middleware(request: Request, call_next):
    if request['path'] in ("/api/register", "/api/login","/api/register/", "/api/login/"):
        response = await call_next(request)
        return response
    body = await request.body()
    body_json = json.loads(body)
    token = body_json.get("token")
    if not token:
        return JSONResponse(
            status_code=200,
            content=ApiResponse(code=400, msg="未携带token")
        )
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RSA256"])
        request.state.user = payload
    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=401,
            content=ApiResponse(code=400, msg="token过期")
        )
    except jwt.InvalidTokenError:
        return JSONResponse(
            status_code=401,
            content=ApiResponse(code=400, msg="token无效")
        )
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=200,
            content=ApiResponse(code=400, msg="token处理错误")
        )
    response = await call_next(request)
    return response

app = FastAPI()
app.middleware("http")(auth_middleware)


DATABASE_URL = config_data['mysql']
engine = sqlalchemy.create_engine(DATABASE_URL)


class UserRegisterPayload(BaseModel):
    uid: str = Field(..., min_length=3, max_length=50, description="手机号")
    username: str = Field(..., min_length=1, max_length=50, description="姓名")
    email: Optional[str] = Field(default="", max_length=200, description="邮箱")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
class UserRegister(ApiRequest):
    payload: UserRegisterPayload
@app.post("/api/register", response_model=ApiResponse)
async def register(req: UserRegister):
    conn = engine.connect()

    result_auth = conn.execute(sqlalchemy.text("SELECT * FROM user_auth WHERE uid = :uid"),
                               {"uid": req.payload.uid})
    result_info = conn.execute(sqlalchemy.text("SELECT * FROM user_info WHERE uid = :uid"),
                               {"uid": req.payload.uid})
    conn.commit()
    if result_info.fetchone() is not None or result_auth.fetchone() is not None:
        return ApiResponse(code=400, msg="手机号已存在")

    try:
        with conn.begin():
            conn.execute(sqlalchemy.text("""
                INSERT INTO user_info (uid, username, email)
                VALUES (:uid, :username, :email);
            """), {
                "uid": req.payload.uid,
                "username": req.payload.username,
                "email": req.payload.email
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
                "uid": req.payload.uid,
                "password": req.payload.password,
                "retry_count": 0,
                "login_time": datetime.utcnow(),
            })
    except Exception as e:
        conn.rollback()
        print(e)
        return ApiResponse(code=500, msg="创建失败")
    finally:
        conn.close()

    return ApiResponse(code=201, msg="注册成功")




class UserLoginPayload(BaseModel):
    uid: str = Field(..., min_length=3, max_length=50, description="手机号")
    password: str = Field(..., min_length=6, description="密码")
class UserLogin(ApiRequest):
    payload: UserLoginPayload
@app.post("/api/login/")
async def login(req: UserLogin):
    conn = engine.connect()
    try:
        result_auth = conn.execute(sqlalchemy.text("SELECT * FROM user_auth WHERE uid = :uid"),
                                   {"uid": req.payload.uid})
        result_info = conn.execute(sqlalchemy.text("SELECT * FROM user_info WHERE uid = :uid"),
                                   {"uid": req.payload.uid})
        conn.commit()
        user_auth = result_auth.fetchone()
        user_info = result_info.fetchone()
        if user_auth is None or user_info is None:
            return ApiResponse(code=404, msg="用户不存在")

        print(user_auth, user_info)
        login_time = user_auth[3]  # login_time
        if login_time > datetime.utcnow():
            time_diff = login_time - datetime.utcnow()
            minutes_diff = int(time_diff.total_seconds() / 60)
            return ApiResponse(code=400, msg=f"请于{minutes_diff}分钟后重试")

        stored_password = user_auth[2]  # password
        if stored_password != req.payload.password:
            if user_auth[4] >= 3:  # retry_count
                login_time = datetime.utcnow() + timedelta(minutes=10)
                conn.execute(sqlalchemy.text("""
                    UPDATE user_auth SET retry_count = 0, login_time = :login_time WHERE uid = :uid
                """), {
                    "login_time": login_time,
                    "uid": req.payload.uid
                })
            else:
                conn.execute(sqlalchemy.text("""
                    UPDATE user_auth SET retry_count = :retry_count WHERE uid = :uid
                """), {
                    "retry_count": user_auth[4] + 1,  # retry_count
                    "uid": req.payload.uid
                })
            conn.commit()
            return ApiResponse(code=400, msg="密码错误")

        expiration_time = datetime.utcnow() + timedelta(hours=24)
        token = jwt.encode(
            {"uid": req.payload.uid, "exp": expiration_time},
            PRIVATE_KEY,
            algorithm="RS256"
        )
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


@app.get("/api/userinfo/{uid}")
async def get_user_info(uid: int, req: ApiRequest):
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config_data['server_port'])
