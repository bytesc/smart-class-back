import sqlalchemy

from .utils.get_config import config_data

DATABASE_URL = config_data['mysql']
engine = sqlalchemy.create_engine(DATABASE_URL)

from .prediction.grade_prediction import predict_for_stu,predict_for_class


def predict_grade_for_stu(user_id: str, lesson_num: str):
    result = predict_for_stu(user_id, lesson_num, engine)
    return result

def predict_grade_for_class(class_name: str, lesson_num: str):
    result = predict_for_class(class_name, lesson_num, engine)
    return result

