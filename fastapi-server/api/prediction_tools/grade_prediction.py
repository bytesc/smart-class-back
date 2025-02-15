import sqlalchemy
import numpy as np
from sklearn.kernel_ridge import KernelRidge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


def get_pre_lessons(lesson_id: str, engine):
    conn = engine.connect()
    try:
        result = conn.execute(sqlalchemy.text("""
                    WITH RECURSIVE SubsequentLessons AS (
                      -- 非递归成员（初始查询）
                      SELECT to_lesson
                      FROM lesson_prerequisite
                      WHERE from_lesson = :lesson_id
                      UNION ALL
                      -- 递归成员
                      SELECT lp.to_lesson
                      FROM lesson_prerequisite lp
                      INNER JOIN SubsequentLessons sl ON lp.from_lesson = sl.to_lesson
                    )
                    -- 最终查询，选择递归CTE的结果
                    SELECT DISTINCT * FROM SubsequentLessons ORDER BY to_lesson;
                                        """),
                              {"lesson_id": lesson_id})

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


def get_grades_for_pre_lessons(lesson_id: str, engine):
    pre_lessons = get_pre_lessons(lesson_id, engine)
    if not pre_lessons:
        return []

    conn = engine.connect()
    try:
        pre_lessons_str = ','.join([f"'{lesson[0]}'" for lesson in pre_lessons])
        query = f"""
            SELECT sg.uid, GROUP_CONCAT(sg.grade ORDER BY sg.lesson_num) AS grades
            FROM stu_grade sg
            WHERE sg.lesson_num IN ({pre_lessons_str})
            GROUP BY sg.uid
            ORDER BY sg.uid;
        """
        result = conn.execute(sqlalchemy.text(query))

        grades_dict = {}
        for row in result.fetchall():
            grades_dict[str(row[0])] = [float(grade) for grade in row[1].split(',')]
        return grades_dict

    except Exception as e:
        print(e)
        raise e
    finally:
        conn.close()


def get_grade(uid: str, lesson_id: str, engine):
    conn = engine.connect()
    try:
        query = sqlalchemy.text("""
            SELECT grade
            FROM stu_grade
            WHERE uid = :uid AND lesson_num = :lesson_id
            ORDER BY id DESC
            LIMIT 1;
        """)
        result = conn.execute(query, {"uid": uid, "lesson_id": lesson_id})

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


def generate_training_dataset(lesson_id: str, engine):
    pre_lesson_grades = get_grades_for_pre_lessons(lesson_id, engine)
    current_lesson_grades = {}
    for uid in pre_lesson_grades.keys():
        grade = get_grade(uid, lesson_id, engine)
        if grade is not None:
            current_lesson_grades[uid] = grade

    x = []
    y = []
    for uid, grades in pre_lesson_grades.items():
        if uid in current_lesson_grades:
            x.append(grades)
            y.append(current_lesson_grades[uid])

    return x, y


def train_and_evaluate_model(X, y, test_size=0.2, random_state=None, alpha=1.0, kernel='rbf', gamma=0.1):
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
# 然后使用train_and_evaluate_model函数训练和评估模型
# 最后使用predict_new_data函数预测新数据
def predict_for_stu(user_id: str, lesson_id: str, engine):
    X, y = generate_training_dataset(lesson_id, engine)
    X = np.array(X)
    y = np.array(y)
    model = train_and_evaluate_model(X, y)
    pre_lesson_grades = get_grades_for_pre_lessons(lesson_id, engine)
    if user_id not in pre_lesson_grades:
        print(f"No grades found for user {user_id} in pre-lessons of {lesson_id}")
        return None
    user_grades = np.array([pre_lesson_grades[user_id]])
    predicted_grade = predict_new_data(model, user_grades)
    return predicted_grade[0]


def predict_for_class(class_name: str, lesson_id: str, engine):
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
    X, y = generate_training_dataset(lesson_id, engine)
    X = np.array(X)
    y = np.array(y)
    # 训练和评估模型
    model = train_and_evaluate_model(X, y)
    # 获取班级学生的前置课程成绩
    pre_lesson_grades = get_grades_for_pre_lessons(lesson_id, engine)
    user_grades_list = []
    uid_has_grades = []
    # 准备预测数据
    for user_id in uid_in_class:
        if user_id in pre_lesson_grades:
            user_grades_list.append(pre_lesson_grades[user_id])
            uid_has_grades.append(user_id)
    # 如果没有学生有前置课程成绩，则返回空列表
    if len(user_grades_list) == 0:
        print(f"No grades found for any student in class {class_name} for pre-lessons of {lesson_id}")
        return []
    # 预测班级学生的成绩
    user_grades_array = np.array(user_grades_list)
    predicted_grades = predict_new_data(model, user_grades_array)
    print(predicted_grades, uid_has_grades)
    # 将预测结果与用户ID对应起来
    predicted_grades_dict = {uid_has_grades[i]: predicted_grades[i] for i in range(len(uid_has_grades))}
    return predicted_grades_dict
