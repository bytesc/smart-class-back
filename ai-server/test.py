# test
from agent.tools.tools_def import predict_grade_for_stu,predict_grade_for_class
from agent.tools.tools_def import query_database

if __name__ == "__main__":
    # r1 = predict_grade_for_stu("18988889999", "DWDwwdwq")
    # print(r1, type(r1))
    # r2 = predict_grade_for_class("计211", "DWDwwdwq")
    # print(r2, type(r2))
    r3 = query_database("计211班级的成绩")
    print(r3, type(r3))
