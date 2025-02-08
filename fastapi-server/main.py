import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
import uvicorn
from starlette.responses import JSONResponse


# 定义统一的响应模型
class ApiResponse(BaseModel):
    code: int = Field(default=200, description="状态码")
    data: dict = Field(default={}, description="数据内容")
    msg: str = Field(default="成功", description="消息")


# 定义学生数据模型
class Student(BaseModel):
    uid: str
    stuNum: str
    stuName: str

# 定义班级数据模型
class ClassStuData(BaseModel):
    classTeacher: str
    classTeacherId: str
    classStuList: List[Student]

app = FastAPI()

# 数据库连接配置
DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/smart_class2"

# 创建数据库引擎
engine = sqlalchemy.create_engine(DATABASE_URL)


@app.get("/class-stu/list-data/{class_name}")
async def get_class_data(class_name: str):
    try:
        # 查询班导师名字
        sql_teacher = f"""
            SELECT ud.username AS classTeacher, ud.uid AS classTeacherId
            FROM class c
            LEFT JOIN user_detail ud ON c.class_teacher_id = ud.uid
            WHERE c.class_name = '{class_name}'
            """

        # 查询学生列表
        sql_students = f"""
            SELECT s.uid, s.stu_num AS stuNum, ud.username AS stuName
            FROM stu_detail s
            LEFT JOIN user_detail ud ON s.uid = ud.uid
            WHERE s.stu_class = '{class_name}'
            """

        # 执行查询
        with engine.connect() as conn:
            # 查询班导师
            result_teacher = conn.execute(sqlalchemy.text(sql_teacher)).fetchone()
            # 查询学生列表
            result_students = conn.execute(sqlalchemy.text(sql_students)).fetchall()

        # 处理查询结果
        classTeacher = result_teacher.classTeacher if result_teacher else None
        classTeacherId = result_teacher.classTeacherId if result_teacher else None
        classStuList = [Student(uid=row.uid, stuNum=row.stuNum, stuName=row.stuName) for row in result_students]

        # 创建班级数据模型实例
        class_data = ClassStuData(classTeacher=classTeacher,
                                  classTeacherId=classTeacherId,
                                  classStuList=classStuList)

        response_data = ApiResponse(code=200, data=class_data.dict(), msg="成功")

    except Exception as e:
        # 如果发生异常，返回错误信息
        response_data = ApiResponse(code=500, data={}, msg=str(e))

    return JSONResponse(content=response_data.dict())



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
