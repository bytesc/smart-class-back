from fastapi import Request

from starlette.responses import JSONResponse

import jwt

from .api_model.response_model import ApiResponse
from .utils.rsa.keys import PUBLIC_KEY


async def authMidware(request: Request, call_next, engine):
    if request['path'] in ("/api/register", "/api/login", "/api/register/", "/api/login/"):
        response = await call_next(request)
        return response
    token = request.headers.get("token")
    if not token or token == "":
        return JSONResponse(
            status_code=200,
            content=ApiResponse(code=400, msg="未携带token").dict()
        )
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
        request.state.user = payload
    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=200,
            content=ApiResponse(code=400, msg="token过期").dict()
        )
    except jwt.InvalidTokenError:
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
    return response
