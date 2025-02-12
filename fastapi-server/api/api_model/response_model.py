
from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    code: int = Field(default=200, description="状态码")
    data: dict = Field(default={}, description="数据内容")
    msg: str = Field(default="", description="消息")
    hidden_msg: str = Field(default="", description="后台消息")
    # token: str = Field(default="", description="Token")
