from django.db import models


class Userinfo(models.Model):
    uid = models.CharField(max_length=32, primary_key=True, verbose_name='用户ID')
    open_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='开放ID')
    password = models.CharField(max_length=255, verbose_name='密码')

    class Meta:
        db_table = 'userinfo'
        verbose_name = '用户信息'
        verbose_name_plural = '01-用户信息列表'

    def __str__(self):
        return str(self.uid)


class UserDetail(models.Model):
    uid = models.OneToOneField(Userinfo, on_delete=models.CASCADE, primary_key=True, db_column='uid',
                               verbose_name='用户ID')
    username = models.CharField(max_length=255, verbose_name='用户名')
    user_gender = models.CharField(max_length=255, null=True, blank=True, verbose_name='性别')
    user_birthday = models.DateField(null=True, blank=True, verbose_name='生日')
    user_notes = models.CharField(max_length=255, null=True, blank=True, verbose_name='备注')

    class Meta:
        db_table = 'user_detail'
        verbose_name = '用户详情'
        verbose_name_plural = '02-用户详情列表'

    def __str__(self):
        return str(self.uid) + str(self.username)


class Class(models.Model):
    class_name = models.CharField(max_length=255, primary_key=True, verbose_name='班级名称')
    class_teacher_id = models.ForeignKey(Userinfo, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='teacher_classes', db_column='class_teacher_id',
                                         verbose_name='班主任')
    class_notes = models.CharField(max_length=255, null=True, blank=True, verbose_name='备注')

    class Meta:
        db_table = 'class'
        verbose_name = '班级'
        verbose_name_plural = '06-班级列表'

    def __str__(self):
        return str(self.class_name)


class StuDetail(models.Model):
    uid = models.OneToOneField(Userinfo, on_delete=models.CASCADE, primary_key=True, db_column='uid',
                               verbose_name='用户ID')
    stu_num = models.CharField(max_length=255, verbose_name='学号')
    stu_major = models.CharField(max_length=255, null=True, blank=True, verbose_name='专业')
    stu_notes = models.CharField(max_length=255, null=True, blank=True, verbose_name='备注')
    stu_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True, db_column='stu_class',
                                  verbose_name='班级')

    class Meta:
        db_table = 'stu_detail'
        verbose_name = '学生详情'
        verbose_name_plural = '03-学生详情列表'

    def __str__(self):
        return str(self.uid) + str(self.stu_num)


class TeacherDetail(models.Model):
    uid = models.OneToOneField(Userinfo, on_delete=models.CASCADE, primary_key=True, db_column='uid',
                               verbose_name='用户ID')
    teacher_num = models.CharField(max_length=255, verbose_name='教师编号')
    teacher_notes = models.CharField(max_length=255, verbose_name='教师备注', null=True, blank=True)

    class Meta:
        db_table = 'teacher_detail'
        verbose_name = '教师详情'
        verbose_name_plural = '04-教师详情列表'

    def __str__(self):
        return str(self.uid) + str(self.teacher_num)


class ClassLeader(models.Model):
    uid = models.ForeignKey(Userinfo, on_delete=models.CASCADE, verbose_name='用户ID')
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name='班级名称')
    position = models.CharField(max_length=255, verbose_name='职务')

    class Meta:
        db_table = 'class_leader'
        verbose_name = '班干部'
        verbose_name_plural = '05-班干部列表'

    def __str__(self):
        return f"{self.uid} - {self.class_name} - {self.position}"


class LessonInfo(models.Model):
    lesson_id = models.CharField(max_length=255, verbose_name='课程编号', primary_key=True, db_column='lesson_id')
    lesson_name = models.CharField(max_length=255, verbose_name='课程名称')
    lesson_notes = models.CharField(max_length=255, verbose_name='课程备注', null=True, blank=True)
    prerequisites = models.ManyToManyField(
        'self',
        through='LessonPrerequisite',
        symmetrical=False,
        related_name='subsequent_lessons',
        blank=True
    )

    class Meta:
        db_table = 'lesson_info'
        verbose_name = '课程'
        verbose_name_plural = '07-课程列表'

    def __str__(self):
        return str(self.lesson_id) + str(self.lesson_name)


class LessonPrerequisite(models.Model):
    from_lesson = models.ForeignKey(LessonInfo, on_delete=models.CASCADE,
                                    related_name='from_lessons', verbose_name='课程')
    to_lesson = models.ForeignKey(LessonInfo, on_delete=models.CASCADE, related_name='to_lessons'
                                  , verbose_name='前序课程')
    notes = models.CharField(max_length=255, null=True, blank=True, verbose_name='备注')

    class Meta:
        db_table = 'lesson_prerequisite'
        verbose_name = '课程前序关系'
        verbose_name_plural = '08-课程前序关系列表'

    def __str__(self):
        return f"{self.from_lesson.lesson_name} -> {self.to_lesson.lesson_name}"


class StuGrade(models.Model):
    uid = models.ForeignKey(Userinfo, on_delete=models.CASCADE, verbose_name='用户ID')
    lesson_id = models.ForeignKey(LessonInfo, on_delete=models.CASCADE, verbose_name='课程编号')
    grade = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='成绩')
    notes = models.CharField(max_length=255, null=True, blank=True, verbose_name='备注')
    semester = models.CharField(max_length=50, verbose_name='学期')

    class Meta:
        db_table = 'stu_grade'
        verbose_name = '学生成绩'
        verbose_name_plural = '09-学生成绩列表'
        unique_together = ('uid', 'lesson_id', 'semester')

    def __str__(self):
        return f"{self.uid} - {self.lesson_id.lesson_name} - {self.semester}"




