from django.db import models
from django.contrib.auth.hashers import check_password, make_password
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime
import uuid


class Group(models.Model):
    group_name = models.CharField(max_length=255)
    department_name = models.CharField(max_length=255)
    course_number = models.IntegerField(validators=[MaxValueValidator(6), MinValueValidator(1)])


class User(models.Model):
    FIO = models.CharField(max_length=255, blank=False)
    e_mail = models.EmailField(blank=True)
    password = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=11, blank=True)
    hometown = models.CharField(max_length=255, blank=True)
    person_info = models.TextField(max_length=2000, blank=True)

    vk_link = models.URLField(blank=True) # TODO unique
    facebook_link = models.URLField(blank=True)
    linkedin_link = models.URLField(blank=True)
    instagram_link = models.URLField(blank=True)

    verification_code = models.CharField(max_length=100, blank=False, default=uuid.uuid1)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()
        return self

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class Teacher(User):
    class Meta:
        ordering = []


class Student(User):
    class Meta:
        ordering = []

    BACHELOR = "BC"
    MASTER = "MR"
    POSTGRADUATE = "PG"
    DEGREES = (
        (BACHELOR, 'Bachelor'),
        (MASTER, 'Master'),
        (POSTGRADUATE, 'Postgraduate')
    )

    FULL_TIME = "FT"
    EXTRAMURAL = "EM"
    EVENING = "EG"
    FORMS_OF_STUDY = (
        (FULL_TIME, 'Full-time'),
        (EXTRAMURAL, 'Extramural'),
        (EVENING, 'Evening')
    )

    CONTRACT = "CT"
    BUDGET = "BG"
    LEARNING_BASES = (
        (CONTRACT, "Contract"),
        (BUDGET, "Budget")
    )

    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=False)
    admission_year = models.DateTimeField(default=datetime.datetime.now, blank=False)
    degree = models.CharField(max_length=2, choices=DEGREES, blank=False)
    form_of_study = models.CharField(max_length=2, choices=FORMS_OF_STUDY, blank=False)
    learning_base = models.CharField(max_length=2, choices=LEARNING_BASES, blank=False)


class Course(models.Model):
    course_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=2000, blank=True)
    course_instructors = models.ManyToManyField(Teacher, related_name="instructors", blank=True)
    trusted_individuals = models.ManyToManyField(Student, related_name="trusted_individuals", blank=True)
    groups_of_course = models.ManyToManyField(Group, blank=True)


class CourseMaterial(models.Model):
    material_name = models.CharField(max_length=100, unique=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField(max_length=2000)
    start_date = models.DateTimeField(default=datetime.datetime.now())


class Task(models.Model):
    task_name = models.CharField(max_length=200, unique=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    start = models.DateTimeField(blank=True)
    end = models.DateTimeField(blank=True)
    description = models.TextField(max_length=2000)


class TaskSolution(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    solution = models.TextField(max_length=2000)


class AccessToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=256, blank=False, unique=True)
    date_login = models.DateTimeField(default=datetime.datetime.now)
