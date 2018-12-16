from django.contrib import admin

from .models import *


class StudentAdmin(admin.ModelAdmin):
    readonly_fields = ["verification_code"]
    list_display = ['FIO', 'admission_year']


class TeacherAdmin(admin.ModelAdmin):
    readonly_fields = ["verification_code"]
    list_display = ['FIO']


class GroupAdmin(admin.ModelAdmin):
    list_display = ['group_name', 'department_name']


class CourseAdmin(admin.ModelAdmin):
    list_display = ['course_name']


admin.site.register(Group, GroupAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Student, StudentAdmin)
