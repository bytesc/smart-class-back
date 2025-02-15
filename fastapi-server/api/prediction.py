import jwt
import sqlalchemy
from fastapi import Request
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta

from starlette.responses import JSONResponse

from .api_model.response_model import ApiResponse
from .utils.rsa.keys import PRIVATE_KEY
from .utils.rsa.token import create_access_token
from .user import get_user_info


from .prediction_tools.grade_prediction import predict_for_class


class ClassGradePredictionModel(BaseModel):
    class_name: str = Field(..., min_length=1, max_length=255, description="班级名称")
    lesson_id: str = Field(..., min_length=1, max_length=255, description="课程id")


async def class_grade_prediction_api(request: Request, data: ClassGradePredictionModel, engine):
    conn = engine.connect()
    try:
        predict_result = predict_for_class(data.class_name,data.lesson_id,engine)
        return ApiResponse(code=200,
                           data=predict_result,
                           msg="预测成功")

    except Exception as e:
        print(e)
        # raise e
        return ApiResponse(code=500, msg="预测错误")
    finally:
        conn.close()
