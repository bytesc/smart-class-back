import sqlalchemy
from fastapi import Request
from pydantic import BaseModel, Field

from .api_model.response_model import ApiResponse


async def get_policy_list(engine):
    conn = engine.connect()
    try:
        response = ApiResponse(code=200,
                               data={
                               },
                               msg="查询成功")

        policy_list_result = conn.execute(sqlalchemy.text("""
                                SELECT policy_name, publish_time
                                FROM policy
                            """), {
            "uid": ""
        })
        conn.commit()
        policy_list = policy_list_result.fetchall()
        print(policy_list)
        if policy_list:
            response.data = {
                "policy_list": [
                    {
                        "policy_name": policy[0],
                        # "content": grade[1],
                        "publish_time": policy[1],
                    } for policy in policy_list
                ]
            }
        return response

    except Exception as e:
        print(e)
        return ApiResponse(code=500, msg="查询政策列表信息发生错误")
    finally:
        conn.close()


async def get_policy_list_api(request: Request, engine):
    response = await get_policy_list(engine)
    return response


async def get_policy_detail(policy_name, engine):
    conn = engine.connect()
    try:
        response = ApiResponse(code=200,
                               data={
                               },
                               msg="查询成功")

        policy_detail_result = conn.execute(sqlalchemy.text("""
                                SELECT policy_name,content, publish_time
                                FROM policy
                                WHERE policy_name=:policy_name
                            """), {
            "policy_name": policy_name
        })
        conn.commit()
        policy_detail = policy_detail_result.fetchone()
        # print(policy_list)
        if policy_detail:
            response.data = {
                        "policy_name": policy_detail[0],
                        "content": policy_detail[1],
                        "publish_time": policy_detail[2]
            }
        return response

    except Exception as e:
        print(e)
        return ApiResponse(code=500, msg="查询政策详情信息发生错误")
    finally:
        conn.close()


async def get_policy_detail_api(request: Request, policy_name: str, engine):
    response = await get_policy_detail(policy_name, engine)
    return response
