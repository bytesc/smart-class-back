import sqlalchemy

from .utils.get_config import config_data
from .utils.llm_access.LLM import get_llm

DATABASE_URL = config_data['mysql']
engine = sqlalchemy.create_engine(DATABASE_URL)

llm = get_llm()

from .prediction.grade_prediction import predict_for_stu_func,predict_for_class_func
from .copilot.sql_code import get_sql_code
from .copilot.utils.read_db import execute_select


def predict_grade_for_stu(user_id: str, lesson_num: str):
    result = predict_for_stu_func(user_id, lesson_num, engine)
    return result

def predict_grade_for_class(class_name: str, lesson_num: str):
    result = predict_for_class_func(class_name, lesson_num, engine)
    return result

def query_database(question):
    sql = get_sql_code(question, llm, engine)
    result = execute_select(engine, sql)
    return result

