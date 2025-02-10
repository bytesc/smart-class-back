from datetime import datetime,timedelta

from fastapi import Request

from starlette.responses import JSONResponse

import jwt

from ..api_model.response_model import ApiResponse
from ..utils.rsa.keys import PUBLIC_KEY

from ..utils.rsa.token import create_access_token, decode_access_token


async def authMidware(request: Request, call_next, engine):
    if request['path'] in ("/api/register", "/api/login", "/api/register/", "/api/login/"):
        response = await call_next(request)
        return response
    token = request.headers.get("token")
    new_token = None
    if not token or token == "":
        return JSONResponse(
            status_code=200,
            content=ApiResponse(code=400, msg="未携带token").dict()
        )
    try:
        payload = decode_access_token(token)
        # print(payload)
        request.state.user = payload
        exp = datetime.utcfromtimestamp(payload['exp'])
        if exp - datetime.utcnow() < timedelta(hours=24):
            new_payload = payload
            new_token = create_access_token(new_payload, timedelta(hours=24))
    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=200,
            content=ApiResponse(code=400, msg="token过期").dict()
        )
    except jwt.InvalidTokenError as e:
        print(e)
        return JSONResponse(
            status_code=200,
            content=ApiResponse(code=400, msg="token无效").dict()
        )
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=200,
            content=ApiResponse(code=400, msg="token处理错误").dict()
        )
    response = await call_next(request)
    if new_token:
        response.headers['new-token'] = new_token
    return response
