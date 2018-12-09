from django.contrib import admin

from .models import *


class StudentAdmin(admin.ModelAdmin):
    readonly_fields = ["verification_code"]


class TeacherAdmin(admin.ModelAdmin):
    readonly_fields = ["verification_code"]


admin.site.register(Group)
admin.site.register(Course)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Student, StudentAdmin)
