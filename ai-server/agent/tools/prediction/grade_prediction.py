import sqlalchemy
import numpy as np
from sklearn.kernel_ridge import KernelRidge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


def get_pre_lessons(lesson_num: str, engine):
    conn = engine.connect()
    try:
        result = conn.execute(sqlalchemy.text("""
                    WITH RECURSIVE SubsequentLessons AS (
                      -- 非递归成员（初始查询）
                      SELECT to_lesson
                      FROM lesson_prerequisite
                      WHERE from_lesson = :lesson_num
                      UNION ALL
                      -- 递归成员
                      SELECT lp.to_lesson
                      FROM lesson_prerequisite lp
                      INNER JOIN SubsequentLessons sl ON lp.from_lesson = sl.to_lesson
                    )
                    -- 最终查询，选择递归CTE的结果
                    SELECT DISTINCT * FROM SubsequentLessons ORDER BY to_lesson;
                                        """),
                              {"lesson_num": lesson_num})

        conn.commit()
        pre_lesson_list = result.fetchall()

        if len(pre_lesson_list) == 0:
            return None
        return pre_lesson_list

    except Exception as e:
        print(e)
        raise e
    finally:
        conn.close()


def get_pre_lessons_grades(lesson_id: str, engine):
    pre_lessons = get_pre_lessons(lesson_id, engine)
    if not pre_lessons:
        return {}

    grades_dict = {}
    for pre_lesson in pre_lessons:
        conn = engine.connect()
        try:
            query = f"""
                   SELECT sg.uid, sg.grade, sg.lesson_num, sg.semester
                   FROM stu_grade sg
                   WHERE sg.lesson_num = '{pre_lesson[0]}'
                   ORDER BY sg.uid,sg.semester;
               """
            result = conn.execute(sqlalchemy.text(query))

            for row in result.fetchall():
                student_id = str(row[0])
                grade = float(row[1])
                if student_id not in grades_dict:
                    grades_dict[student_id] = [None] * len(pre_lessons)
                index = pre_lessons.index(pre_lesson)
                grades_dict[student_id][index] = grade
        except Exception as e:
            print(e)
            raise e
        finally:
            conn.close()

    # 过滤掉那些没有完整成绩记录的学生
    grades_dict = {k: v for k, v in grades_dict.items() if None not in v}

    return grades_dict


def get_grade_for_stu(uid: str, lesson_num: str, engine):
    conn = engine.connect()
    try:
        query = sqlalchemy.text("""
            SELECT grade
            FROM stu_grade
            WHERE uid = :uid AND lesson_num = :lesson_num
            ORDER BY id DESC
            LIMIT 1;
        """)
        result = conn.execute(query, {"uid": uid, "lesson_num": lesson_num})

        row = result.fetchone()
        if row:
            return row[0]
        else:
            return None

    except Exception as e:
        print(e)
        raise e
    finally:
        conn.close()


def generate_training_dataset(lesson_num: str, engine):
    pre_lesson_grades = get_pre_lessons_grades(lesson_num, engine)
    current_lesson_grades = {}
    for uid in pre_lesson_grades.keys():
        grade = get_grade_for_stu(uid, lesson_num, engine)
        if grade is not None:
            current_lesson_grades[uid] = grade

    x = []
    y = []
    for uid, grades in pre_lesson_grades.items():
        if uid in current_lesson_grades:
            x.append(grades)
            y.append(current_lesson_grades[uid])

    return x, y


def train_model(X, y, test_size=0.2, random_state=None, alpha=1.0, kernel='rbf', gamma=0.1):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    kr = KernelRidge(alpha=alpha, kernel=kernel, gamma=gamma)  # 创建核岭回归模型
    kr.fit(X_train, y_train)  # 训练模型
    y_pred = kr.predict(X_test)  # 预测测试集
    mse = mean_squared_error(y_test, y_pred)  # 计算预测的均方误差
    print(f"Mean Squared Error: {mse}")
    return kr


def predict_new_data(model, new_data):
    new_predictions = model.predict(new_data)
    return new_predictions


# 使用generate_training_dataset函数获取特征数据和目标变量
# 然后使用train_model函数训练和评估模型
# 最后使用predict_new_data函数预测新数据
def predict_for_stu_func(user_id: str, lesson_num: str, engine):
    X, y = generate_training_dataset(lesson_num, engine)
    X = np.array(X)
    y = np.array(y)
    model = train_model(X, y)
    pre_lesson_grades = get_pre_lessons_grades(lesson_num, engine)
    if user_id not in pre_lesson_grades:
        print(f"No grades found for user {user_id} in pre-lessons of {lesson_num}")
        return None
    user_grades = np.array([pre_lesson_grades[user_id]])
    predicted_grade = predict_new_data(model, user_grades)
    return predicted_grade[0]


def predict_for_class_func(class_name: str, lesson_num: str, engine):
    # 获取班级中所有学生的user_id
    conn = engine.connect()
    try:
        query = sqlalchemy.text("""
            SELECT stu_detail.uid
            FROM stu_detail
            WHERE stu_detail.class_name = :class_name;
        """)
        result = conn.execute(query, {"class_name": class_name})
        uid_in_class = [row[0] for row in result.fetchall()]
    except Exception as e:
        print(e)
        raise e
    finally:
        conn.close()

    # 获取特征数据和目标变量
    X, y = generate_training_dataset(lesson_num, engine)
    X = np.array(X)
    y = np.array(y)
    # 训练和评估模型
    model = train_model(X, y)
    # 获取班级学生的前置课程成绩
    pre_lesson_grades = get_pre_lessons_grades(lesson_num, engine)
    user_grades_list = []
    uid_has_grades = []
    # 准备预测数据
    for user_id in uid_in_class:
        if user_id in pre_lesson_grades:
            user_grades_list.append(pre_lesson_grades[user_id])
            uid_has_grades.append(user_id)
    # 如果没有学生有前置课程成绩，则返回空
    if len(user_grades_list) == 0:
        print(f"No grades found for any student in class {class_name} for pre-lessons of {lesson_num}")
        return None
    # 预测班级学生的成绩
    user_grades_array = np.array(user_grades_list)
    predicted_grades = predict_new_data(model, user_grades_array)
    # 将预测结果与用户ID对应起来
    predicted_grades_dict = {uid_has_grades[i]: predicted_grades[i] for i in range(len(uid_has_grades))}

    # return predicted_grades_dict
    conn = engine.connect()
    stu_list_result = conn.execute(sqlalchemy.text("""
                        SELECT stu_detail.uid, stu_detail.stu_num, stu_detail.major,
                         stu_detail.stu_position, user_info.username
                        FROM stu_detail, user_info
                        WHERE stu_detail.class_name = :class_name and stu_detail.uid = user_info.uid
                    """), {
        "class_name": class_name
    })
    conn.commit()
    stu_list = stu_list_result.fetchall()
    stu_info_dict = {stu[0]: {"stu_num": stu[1], "username": stu[4]} for stu in stu_list}

    result_list_with_info_list = []
    for uid, predicted_grade in predicted_grades_dict.items():
        stu_info = stu_info_dict.get(uid, {})
        result_list_with_info_list.append({
            "uid": uid,
            "predicted_grade": predicted_grade,
            "stu_num": stu_info.get("stu_num"),
            "username": stu_info.get("username")
        })
    return result_list_with_info_list
