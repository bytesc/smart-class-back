import sqlalchemy
from fastapi import FastAPI
import uvicorn
from api.utils.get_config import config_data

from fastapi import Request

from api.api_model.response_model import ApiResponse

app = FastAPI()


from api.midware.midware import authMidware
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    response = await authMidware(request, call_next, engine)
    return response


DATABASE_URL = config_data['mysql']
engine = sqlalchemy.create_engine(DATABASE_URL)


from api.login import UserRegisterModel, registerApi
@app.post("/api/register", response_model=ApiResponse)
async def register(request: Request, data: UserRegisterModel):
    response = await registerApi(request, data, engine)
    return response


from api.login import UserLoginModel, loginApi
@app.post("/api/login/")
async def login(request: Request, data: UserLoginModel):
    response = await loginApi(request, data, engine)
    return response

from api.user import userInfoApi
@app.post("/api/userinfo/{uid}")
async def get_user_info(request: Request, uid: int):
    response = await userInfoApi(request, uid, engine)
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config_data['server_port'])
