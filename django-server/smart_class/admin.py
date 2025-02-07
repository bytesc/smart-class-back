from django.contrib import admin

# Register your models here.
from django.contrib import admin

admin.site.site_header = 'XXX后台管理'  # 设置header
admin.site.site_title = 'XXX管理后台'   # 设置title
admin.site.index_title = 'XXX管理后台'


from .models import Userinfo, UserDetail, Class, StuDetail, TeacherDetail
from .models import LessonInfo, StuGrade, ClassLeader, LessonPrerequisite

# Register your models here.


class UserinfoAdmin(admin.ModelAdmin):
    list_display = ('uid', 'open_id', 'password')
    search_fields = ('uid', 'open_id')


class UserDetailAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserDetail._meta.fields]
    list_filter = [field.name for field in UserDetail._meta.fields]
    search_fields = [field.name for field in UserDetail._meta.fields]


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


class ClassLeaderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ClassLeader._meta.fields]
    list_filter = [field.name for field in ClassLeader._meta.fields]
    search_fields = [field.name for field in ClassLeader._meta.fields]


class LessonPrerequisiteAdmin(admin.ModelAdmin):
    list_display = [field.name for field in LessonPrerequisite._meta.fields]
    list_filter = [field.name for field in LessonPrerequisite._meta.fields]
    search_fields = [field.name for field in LessonPrerequisite._meta.fields]


admin.site.register(Userinfo, UserinfoAdmin)
admin.site.register(UserDetail, UserDetailAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(StuDetail, StuDetailAdmin)
admin.site.register(TeacherDetail, TeacherDetailAdmin)
admin.site.register(LessonInfo, LessonInfoAdmin)
admin.site.register(StuGrade, StuGradeAdmin)
admin.site.register(ClassLeader, ClassLeaderAdmin)
admin.site.register(LessonPrerequisite, LessonPrerequisiteAdmin)




