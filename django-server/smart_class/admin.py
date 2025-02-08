from django.contrib import admin

# Register your models here.
from django.contrib import admin

admin.site.site_header = '智慧班级后台管理'  # 设置header
admin.site.site_title = '智慧班级后台管理'   # 设置title
admin.site.index_title = '智慧班级后台管理'


from .models import UserAuth, UserInfo, Class, StuDetail, TeacherDetail
from .models import LessonInfo, StuGrade, LessonPrerequisite, Semester
from .models import Announcement, Policy, Message

# Register your models here.


class UserAuthAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserAuth._meta.fields]
    list_filter = [field.name for field in UserAuth._meta.fields]
    search_fields = [field.name for field in UserAuth._meta.fields]


class UserInfoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserInfo._meta.fields]
    list_filter = [field.name for field in UserInfo._meta.fields]
    search_fields = [field.name for field in UserInfo._meta.fields]


class ClassAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Class._meta.fields]
    list_filter = [field.name for field in Class._meta.fields]
    search_fields = [field.name for field in Class._meta.fields]


class StuDetailAdmin(admin.ModelAdmin):
    list_display = [field.name for field in StuDetail._meta.fields]
    list_filter = [field.name for field in StuDetail._meta.fields]
    search_fields = [field.name for field in StuDetail._meta.fields]


class TeacherDetailAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TeacherDetail._meta.fields]
    list_filter = [field.name for field in TeacherDetail._meta.fields]
    search_fields = [field.name for field in TeacherDetail._meta.fields]


class LessonInfoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in LessonInfo._meta.fields]
    list_filter = [field.name for field in LessonInfo._meta.fields]
    search_fields = [field.name for field in LessonInfo._meta.fields]


class StuGradeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in StuGrade._meta.fields]
    list_filter = [field.name for field in StuGrade._meta.fields]
    search_fields = [field.name for field in StuGrade._meta.fields]


class LessonPrerequisiteAdmin(admin.ModelAdmin):
    list_display = [field.name for field in LessonPrerequisite._meta.fields]
    list_filter = [field.name for field in LessonPrerequisite._meta.fields]
    search_fields = [field.name for field in LessonPrerequisite._meta.fields]


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Announcement._meta.fields]
    list_filter = [field.name for field in Announcement._meta.fields]
    search_fields = [field.name for field in Announcement._meta.fields]


class PolicyPrerequisiteAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Policy._meta.fields]
    list_filter = [field.name for field in Policy._meta.fields]
    search_fields = [field.name for field in Policy._meta.fields]


class MessageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Message._meta.fields]
    list_filter = [field.name for field in Message._meta.fields]
    search_fields = [field.name for field in Message._meta.fields]


admin.site.register(UserAuth, UserAuthAdmin)
admin.site.register(UserInfo, UserInfoAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(StuDetail, StuDetailAdmin)
admin.site.register(TeacherDetail, TeacherDetailAdmin)
admin.site.register(LessonInfo, LessonInfoAdmin)
admin.site.register(StuGrade, StuGradeAdmin)
admin.site.register(LessonPrerequisite, LessonPrerequisiteAdmin)
admin.site.register(Semester)
admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(Policy, PolicyPrerequisiteAdmin)
admin.site.register(Message, MessageAdmin)
