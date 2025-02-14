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
async def get_userinfo(request: Request, uid: str):
    response = await get_user_info_api(request, uid, engine)
    return response


from api.my_class import get_class_list_api
@app.post("/api/my-class/{class_name}")
async def get_my_class(request: Request, class_name: str):
    response = await get_class_list_api(request, class_name, engine)
    return response


from api.teacher import get_teacher_class_api
@app.post("/api/teacher-class/{uid}")
async def get_teacher_class(request: Request, uid: str):
    response = await get_teacher_class_api(request, uid, engine)
    return response


from api.my_grade import get_my_grade_list_api
@app.post("/api/stu-grade/{uid}")
async def get_my_grade_list(request: Request, uid: str):
    response = await get_my_grade_list_api(request, uid, engine)
    return response


from api.my_grade import get_class_grade_list_api
@app.post("/api/class-grade/{class_name}")
async def get_my_grade_list(request: Request, class_name: str):
    response = await get_class_grade_list_api(request, class_name, engine)
    return response


from api.policy import get_policy_list_api
@app.post("/api/policy-list/")
async def get_policy_list(request: Request):
    response = await get_policy_list_api(request, engine)
    return response


from api.policy import get_policy_detail_api
@app.post("/api/policy/{policy_name}")
async def get_policy_list(request: Request,policy_name:str):
    response = await get_policy_detail_api(request,policy_name,engine)
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config_data['server_port'])
