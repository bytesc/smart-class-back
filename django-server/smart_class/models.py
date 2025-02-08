from django.db import models
from django.utils import timezone


class UserInfo(models.Model):
    uid = models.CharField(max_length=32, primary_key=True, verbose_name='用户ID')
    username = models.CharField(max_length=255, verbose_name='用户名')
    gender = models.CharField(max_length=255, null=True, blank=True, verbose_name='性别')
    email = models.EmailField(max_length=255, null=True, blank=True, verbose_name='邮箱')
    birthday = models.DateField(null=True, blank=True, verbose_name='生日')
    notes = models.CharField(max_length=255, null=True, blank=True, verbose_name='备注')

    class Meta:
        db_table = 'user_info'
        verbose_name = '用户信息'
        verbose_name_plural = '01-用户信息列表'

    def __str__(self):
        return str(self.uid) + " - " + str(self.username)


class UserAuth(models.Model):
    uid = models.OneToOneField(UserInfo, on_delete=models.CASCADE, primary_key=True, db_column='uid',
                               verbose_name='用户ID')
    open_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='开放ID')
    password = models.CharField(max_length=255, verbose_name='密码')

    class Meta:
        db_table = 'user_auth'
        verbose_name = '用户凭证'
        verbose_name_plural = '02-用户凭证列表'

    def __str__(self):
        return str(self.uid)


class Class(models.Model):
    class_name = models.CharField(max_length=255, primary_key=True, verbose_name='班级名称')
    teacher_uid = models.ForeignKey(UserInfo, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='teacher_classes', db_column='teacher_uid',
                                    verbose_name='班主任')
    notes = models.CharField(max_length=255, null=True, blank=True, verbose_name='备注')

    class Meta:
        db_table = 'class'
        verbose_name = '班级'
        verbose_name_plural = '06-班级列表'

    def __str__(self):
        return str(self.class_name)


class StuDetail(models.Model):
    uid = models.OneToOneField(UserInfo, on_delete=models.CASCADE, primary_key=True, db_column='uid',
                               verbose_name='用户ID')
    stu_num = models.CharField(max_length=255, verbose_name='学号')
    major = models.CharField(max_length=255, null=True, blank=True, verbose_name='专业')
    class_name = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True, db_column='stu_class',
                                   verbose_name='班级')
    stu_position = models.CharField(max_length=255, null=True, blank=True, verbose_name='职务')
    notes = models.CharField(max_length=255, null=True, blank=True, verbose_name='备注')

    class Meta:
        db_table = 'stu_detail'
        verbose_name = '学生详情'
        verbose_name_plural = '03-学生详情列表'

    def __str__(self):
        return str(self.uid) + " - " + str(self.stu_num)


class TeacherDetail(models.Model):
    uid = models.OneToOneField(UserInfo, on_delete=models.CASCADE, primary_key=True, db_column='uid',
                               verbose_name='用户ID')
    teacher_num = models.CharField(max_length=255, verbose_name='教师编号')
    notes = models.CharField(max_length=255, verbose_name='教师备注', null=True, blank=True)

    class Meta:
        db_table = 'teacher_detail'
        verbose_name = '教师详情'
        verbose_name_plural = '04-教师详情列表'

    def __str__(self):
        return str(self.uid) + " - " + str(self.teacher_num)


class LessonInfo(models.Model):
    lesson_num = models.CharField(max_length=255, verbose_name='课程编号', primary_key=True, db_column='lesson_id')
    lesson_name = models.CharField(max_length=255, verbose_name='课程名称')
    notes = models.CharField(max_length=255, verbose_name='课程备注', null=True, blank=True)

    # prerequisites = models.ManyToManyField(
    #     'self',
    #     through='LessonPrerequisite',
    #     symmetrical=False,
    #     related_name='subsequent_lessons',
    #     blank=True
    # )

    class Meta:
        db_table = 'lesson_info'
        verbose_name = '课程'
        verbose_name_plural = '07-课程列表'

    def __str__(self):
        return str(self.lesson_num) + " - " + str(self.lesson_name)


# auto id
class LessonPrerequisite(models.Model):
    from_lesson = models.ForeignKey(LessonInfo, on_delete=models.CASCADE, db_column='from_lesson',
                                    related_name='from_lessons', verbose_name='课程')
    to_lesson = models.ForeignKey(LessonInfo, on_delete=models.CASCADE, db_column='to_lesson',
                                  related_name='to_lessons', verbose_name='前序课程')
    notes = models.CharField(max_length=255, null=True, blank=True, verbose_name='备注')

    class Meta:
        db_table = 'lesson_prerequisite'
        verbose_name = '课程前序关系'
        verbose_name_plural = '08-课程前序关系列表'

    def __str__(self):
        return f"{self.from_lesson} -> {self.to_lesson}"


class Semester(models.Model):
    semester_name = models.CharField(max_length=255, verbose_name='学期名称', unique=True, primary_key=True)
    start_date = models.DateField(verbose_name='开始日期', null=True, blank=True)
    end_date = models.DateField(verbose_name='结束日期', null=True, blank=True)
    notes = models.CharField(max_length=255, null=True, blank=True, verbose_name='备注')

    class Meta:
        db_table = 'semester'
        verbose_name = '学期'
        verbose_name_plural = '05-学期列表'

    def __str__(self):
        return self.semester_name


# auto id
class StuGrade(models.Model):
    uid = models.ForeignKey(UserInfo, on_delete=models.CASCADE,
                            db_column='uid', verbose_name='用户ID')
    lesson_num = models.ForeignKey(LessonInfo, on_delete=models.CASCADE,
                                  db_column='lesson_num', verbose_name='课程编号')
    grade = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='成绩')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE,
                                 db_column='semester', verbose_name='学期')
    notes = models.CharField(max_length=255, null=True, blank=True, verbose_name='备注')

    class Meta:
        db_table = 'stu_grade'
        verbose_name = '学生成绩'
        verbose_name_plural = '09-学生成绩列表'
        unique_together = ('uid', 'lesson_num', 'semester')

    def __str__(self):
        return f"{self.uid} - {self.lesson_num} - {self.semester}"


class Announcement(models.Model):
    announcement_name = models.CharField(max_length=255, primary_key=True, verbose_name='公告名称')
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, db_column='class_name', verbose_name='班级')
    publisher = models.ForeignKey(UserInfo, on_delete=models.CASCADE, db_column='publisher_uid', verbose_name='发布人')
    publish_time = models.DateTimeField(default=timezone.now, verbose_name='发布时间', null=True, blank=True)
    content = models.TextField(verbose_name='公告内容')

    class Meta:
        db_table = 'announcement'
        verbose_name = '公告'
        verbose_name_plural = '10-班级公告列表'

    def __str__(self):
        return f"{self.announcement_name} - {self.class_name} - {self.publisher}"


class Policy(models.Model):
    policy_name = models.CharField(max_length=255, verbose_name='政策名称', primary_key=True)
    content = models.TextField(verbose_name='政策内容')
    publish_time = models.DateTimeField(default=timezone.now, verbose_name='发布时间', null=True, blank=True)

    class Meta:
        db_table = 'policy'
        verbose_name = '政策'
        verbose_name_plural = '00-政策列表'

    def __str__(self):
        return self.policy_name
