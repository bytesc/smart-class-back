import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
import uvicorn
from starlette.responses import JSONResponse
from utils.get_config import config_data

# 定义统一的响应模型
class ApiResponse(BaseModel):
    code: int = Field(default=200, description="状态码")
    data: dict = Field(default={}, description="数据内容")
    msg: str = Field(default="成功", description="消息")


app = FastAPI()

# 数据库连接配置
DATABASE_URL = config_data['mysql']

# 创建数据库引擎
engine = sqlalchemy.create_engine(DATABASE_URL)





if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config_data['server_port'])
