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


from api.login import UserRegisterModel, register_api
@app.post("/api/register", response_model=ApiResponse)
async def register(request: Request, data: UserRegisterModel):
    response = await register_api(request, data, engine)
    return response


from api.login import UserLoginModel, login_api
@app.post("/api/login/")
async def login(request: Request, data: UserLoginModel):
    response = await login_api(request, data, engine)
    return response


from api.user import get_user_info_api
@app.post("/api/userinfo/{uid}")
async def get_user_info(request: Request, uid: str):
    response = await get_user_info_api(request, uid, engine)
    return response


from api.my_class import get_class_list_api
@app.post("/api/my-class/{class_name}")
async def get_user_info(request: Request, class_name: str):
    response = await get_class_list_api(request, class_name, engine)
    return response


from api.teacher import get_teacher_class_api
@app.post("/api/teacher-class/{uid}")
async def get_user_info(request: Request, uid: str):
    response = await get_teacher_class_api(request, uid, engine)
    return response



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config_data['server_port'])
