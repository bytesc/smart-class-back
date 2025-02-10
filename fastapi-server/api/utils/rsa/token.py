import jwt
import sqlalchemy
from fastapi import Request
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta
from .keys import PRIVATE_KEY,PUBLIC_KEY


def create_access_token(token_payload: dict, expiration_delta: timedelta = timedelta(hours=24)) -> str:
    """
    创建访问令牌
    :param token_payload: JWT payload 字典
    :param expiration_delta: 令牌过期时间
    :return: 签发的JWT令牌
    """
    expiration_time = datetime.utcnow() + expiration_delta
    token_payload['exp'] = expiration_time

    token = jwt.encode(
        token_payload,
        PRIVATE_KEY,
        algorithm="RS256"
    )
    return token


def decode_access_token(token:str):
    payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
    return payload
