from django.test import TestCase
from django.urls import reverse
from lms_app.urls import urlpatterns
from .. import views
from ..models import *


class AuthTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User(e_mail='foo@example.com')
        user.set_password("password1")
        user.save()

    def test_success_auth(self):
        data = {'email': 'foo@example.com', 'password': 'password1'}
        resp = self.client.post(reverse('lms_app:auth'), data)
        self.assertEqual(resp.status_code, 200)

    def test_bad_password(self):
        data = {'email': 'foo@example.com', 'password': 'password2'}
        resp = self.client.post(reverse('lms_app:auth'), data)
        self.assertEqual(resp.status_code, 406)

    def test_no_user(self):
        data = {'email': 'foo1@example.com', 'password': 'password2'}
        resp = self.client.post(reverse('lms_app:auth'), data)
        self.assertEqual(resp.status_code, 404)

    def test_bad_request(self):
        data = {'EMAIL': 'foo@example.com', 'password': 'password1'}
        resp = self.client.post(reverse('lms_app:auth'), data)
        self.assertEqual(resp.status_code, 400)


class RegistrationTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User(FIO="Knyazev Alexander")
        user.save()

    def test_success_registration(self):
        user = User.objects.get(id=1)
        code = user.verification_code

        data = {'verification_code': code, 'email': 'foo@example.com', 'password': 'password1'}
        resp = self.client.post(reverse('lms_app:registration'), data)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(User.objects.get(id=1).e_mail, data['email'])

    def test_bad_verification_code(self):
        user = User.objects.get(id=1)
        code = user.verification_code

        data = {'verification_code': "----", 'email': 'foo@example.com', 'password': 'password1'}
        resp = self.client.post(reverse('lms_app:registration'), data)
        self.assertEqual(resp.status_code, 404)

    def test_bad_request(self):
        user = User.objects.get(id=1)
        code = user.verification_code

        data = {'verification_code': code, 'email': 'foo@example.com'}
        resp = self.client.post(reverse('lms_app:registration'), data)
        self.assertEqual(resp.status_code, 400)

    def test_bad_email(self):
        user = User.objects.get(id=1)
        code = user.verification_code

        data = {'verification_code': code, 'email': 'fooexample', 'password': 'password1'}
        resp = self.client.post(reverse('lms_app:registration'), data)
        self.assertEqual(resp.status_code, 403)
        self.assertTrue('answer' in resp.json())
        self.assertEqual(resp.json()['answer'], "Bad e-mail")

    def test_bad_password(self):
        user = User.objects.get(id=1)
        code = user.verification_code

        data = {'verification_code': code, 'email': 'foo@example.com', 'password': '1234'}
        resp = self.client.post(reverse('lms_app:registration'), data)
        self.assertEqual(resp.status_code, 403)


class MyProfileWatchTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User(FIO="Knyazev Alexander", e_mail='foo@example.com')
        user.set_password('password1')
        user.save()
        access_token = AccessToken()
        access_token.user = user
        access_token.token = '123456'
        access_token.save()

    def test_success_case(self):
        data = {'token': '123456'}
        resp = self.client.get(reverse('lms_app:get_my_profile'), data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('FIO' in resp.json())
        self.assertEqual(resp.json()['FIO'], 'Knyazev Alexander')

    def test_invalid_token(self):
        data = {'token': '12345678'}
        resp = self.client.get(reverse('lms_app:get_my_profile'), data)
        self.assertEqual(resp.status_code, 401)


class MyProfileEditTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User(FIO="Knyazev Alexander", e_mail='foo@example.com', password='password1')
        user.save()
        access_token = AccessToken()
        access_token.user = user
        access_token.token = '123456'
        access_token.save()

    def test_success_case(self):
        data = {'token': '123456', 'link_to_profile':["https://vk.com/example"], 'phone_number': '+79671219023',
                'person_info': 'I am student', 'hometown': 'Moscow', 'password': 'password2',
                'old_password': 'password1'}
        resp = self.client.post(reverse('lms_app:edit_my_profile'), data)
        self.assertEqual(resp.status_code, 200)

    def test_invalid_token(self):
        data = {'token': '12345678', 'link_to_profile':["https://vk.com/example"], 'phone_number': '+79671219023',
                'person_info': 'I am student', 'hometown': 'Moscow'}
        resp = self.client.post(reverse('lms_app:edit_my_profile'), data)
        self.assertEqual(resp.status_code, 401)

    def test_invalid_profile_link(self):
        data = {'token': '12345678', 'link_to_profile':["vk.com/example"], 'phone_number': '+79671219023',
                'person_info': 'I am student', 'hometown': 'Moscow'}
        resp = self.client.post(reverse('lms_app:edit_my_profile'), data)
        self.assertEqual(resp.status_code, 400)

    def test_invalid_phone_number(self):
        data = {'token': '12345678', 'link_to_profile':["vk.com/example"], 'phone_number': '89671219023',
                'person_info': 'I am student', 'hometown': 'Moscow'}
        resp = self.client.post(reverse('lms_app:edit_my_profile'), data)
        self.assertEqual(resp.status_code, 400)

    def test_not_editable_field(self):
        data = {'token': '12345678', 'fio': 'Knyazev Aleksandr', 'link_to_profile':["vk.com/example"], 'phone_number': '89671219023',
                'person_info': 'I am student', 'hometown': 'Moscow'}
        resp = self.client.post(reverse('lms_app:edit_my_profile'), data)
        self.assertEqual(resp.status_code, 400)

    def test_failed_password_change(self):
        data = {'token': '12345678', 'password': 'password2'}
        resp = self.client.post(reverse('lms_app:edit_my_profile'), data)
        self.assertEqual(resp.status_code, 400)

    def test_failed_password_change2(self):
        data = {'token': '12345678', 'password': 'password2', 'old_password': 'password0'}
        resp = self.client.post(reverse('lms_app:edit_my_profile'), data)
        self.assertEqual(resp.status_code, 400)


class GetUserProfileTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User(FIO="Knyazev Alexander", e_mail='foo@example.com', password='password1')
        user.save()
        access_token = AccessToken()
        access_token.user = user
        access_token.token = '123456'
        access_token.save()

        user2 = User(FIO="Kotov Sergey", e_mail='foo2@example.com', password='password2',
                                    vk_link='https://vk.com/KS')
        user2.save()

    def test_success_access_by_id(self):
        data = {'token': '123456', 'user_id': 1}
        resp = self.client.get(reverse('lms_app:get_user_profile'), data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["FIO"], "Kotov Sergey")

    def test_success_access_by_link(self):
        data = {'token': '123456', 'link_to_user': 'https://vk.com/KS'}
        resp = self.client.get(reverse('lms_app:get_user_profile'), data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["FIO"], "Kotov Sergey")

    def test_bad_token(self):
        data = {'token': '1234567', 'link_to_user': 'https://vk.com/KS'}
        resp = self.client.get(reverse('lms_app:get_user_profile'), data)
        self.assertEqual(resp.status_code, 401)

    def test_bad_link(self):
        data = {'token': '123456', 'link_to_user': 'https://vk.com/KSergey'}
        resp = self.client.get(reverse('lms_app:get_user_profile'), data)
        self.assertEqual(resp.status_code, 404)

    def test_bad_userid(self):
        data = {'token': '123456', 'user_id': 10}
        resp = self.client.get(reverse('lms_app:get_user_profile'), data)
        self.assertEqual(resp.status_code, 404)

    def test_bad_request(self):
        data = {'token': '123456', 'fio': 'Kotov Sergey'}
        resp = self.client.get(reverse('lms_app:get_user_profile'), data)
        self.assertEqual(resp.status_code, 400)


class GetClassmatesTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        group = Group(group_name="492", department_name="diht", course_number=4)
        group.save()
        student1 = Student(FIO="Knyazev Alexander", e_mail='foo@example.com', password='password1',
                                          degree='Bachelor', form_of_study='Full-time', learning_base='Budget',
                                          group=group)
        student1.save()

        access_token = AccessToken()
        access_token.user = student1
        access_token.token = '123456'
        access_token.save()

        student2 = Student(FIO="Alexey", e_mail='foo2@example.com', password='password2',
                                          degree='Bachelor', form_of_study='Full-time', learning_base='Budget',
                                          group=group)
        student2.save()

        student3 = Student(FIO="Vladimir", e_mail='foo3@example.com', password='password3',
                                          degree='Bachelor', form_of_study='Full-time', learning_base='Budget',
                                          group=group)
        student3.save()

    def test_success_case(self):
        data = {'token': '123456'}
        resp = self.client.get(reverse('get_classmates'), data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 2)

    def test_bad_token(self):
        data = {'token': '1234567'}
        resp = self.client.get(reverse('get_classmates'), data)
        self.assertEqual(resp.status_code, 401)


class GetCoursesListTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        group = Group(group_name="492", department_name="diht", course_number=4)
        group.save()
        student = Student(FIO="Knyazev Alexander", e_mail='foo@example.com', password='password1',
                                          degree='Bachelor', form_of_study='Full-time', learning_base='Budget',
                                          group=group)
        student.save()

        access_token = AccessToken()
        access_token.user = student
        access_token.token = '123456'
        access_token.save()

        teacher = Teacher(FIO="Ivanov Yuri", e_mail='foo2@example.com', password='password2')
        teacher.save()

        access_token2 = AccessToken()
        access_token2.user = teacher
        access_token2.token = '123457'
        access_token2.save()

        course1 = Course(course_name="Matan")
        course1.groups_of_course.add(group)
        course1.course_instructors.add(teacher)
        course1.save()
        course2 = Course(course_name="English")
        course2.groups_of_course.add(group)
        course2.course_instructors.add(teacher)
        course2.save()

    def test_success_student_case(self):
        data = {'token': '123456'}
        resp = self.client.get(reverse('get_courses_list'), data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('list_of_courses' in resp.context)
        self.assertEqual(len(resp.context['list_of_courses']), 2)

    def test_success_teacher_case(self):
        data = {'token': '123457'}
        resp = self.client.get(reverse('get_courses_list'), data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('list_of_courses' in resp.context)
        self.assertEqual(len(resp.context['list_of_courses']), 2)

    def test_bad_token(self):
        data = {'token': '123'}
        resp = self.client.get(reverse('get_courses_list'), data)
        self.assertEqual(resp.status_code, 401)


class GetCourseInfoTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        group = Group(group_name="492", department_name="diht", course_number=4)
        group.save()
        student = Student(FIO="Knyazev Alexander", e_mail='foo@example.com', password='password1',
                                          degree='Bachelor', form_of_study='Full-time', learning_base='Budget',
                                          group=group)
        student.save()

        access_token = AccessToken()
        access_token.user = student
        access_token.token = '123456'
        access_token.save()

        course = Course(course_name='Matan', description='---')
        course.groups_of_course.add(group)
        course.save()

    def test_success_case(self):
        data = {'token': '123456', 'course_name': 'Matan'}
        resp = self.client.get(reverse('get_course_info'), data)
        self.assertEqual(resp.status_code, 200)

    def test_invalid_course_name(self):
        data = {'token': '123456', 'course_name': 'Linal'}
        resp = self.client.get(reverse('get_course_info'), data)
        self.assertEqual(resp.status_code, 404)

    def test_bad_token(self):
        data = {'token': '12345678', 'course_name': 'Matan'}
        resp = self.client.get(reverse('get_course_info'), data)
        self.assertEqual(resp.status_code, 401)


class ManageCourseMaterialTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        group = Group(group_name="492", department_name="diht", course_number=4)
        group.save()
        student = Student(FIO="Knyazev Alexander", e_mail='foo@example.com', password='password1',
                                          degree='Bachelor', form_of_study='Full-time', learning_base='Budget',
                                          group=group)
        student.save()

        access_token = AccessToken()
        access_token.user = student
        access_token.token = '123456'
        access_token.save()

        teacher = Teacher(FIO="Ivanov Yuri", e_mail='foo2@example.com', password='password2')
        teacher.save()

        access_token2 = AccessToken()
        access_token2.user = teacher
        access_token2.token = '123457'
        access_token2.save()

        course = Course(course_name='Matan', description='---')
        course.groups_of_course.add(group)
        course.trusted_individuals.add(student)
        course.course_instructors.add(teacher)
        course.save()

        course_material = CourseMaterial(material_name="Lecture 1", course=course, content='Intro')
        course_material.save()

    def test_success_add_by_teacher(self):
        data = {'token': '123457', 'course_name': 'Matan', 'course_material_name': 'Lecture 2',
                'course_material_body': 'No info'}
        resp = self.client.post(reverse('manage_course_materials'), data)
        self.assertEqual(resp.status_code, 200)

    def test_success_add_by_student(self):
        data = {'token': '123456', 'course_name': 'Matan', 'course_material_name': 'Lecture 2',
                'course_material_body': 'No info'}
        resp = self.client.post(reverse('manage_course_materials'), data)
        self.assertEqual(resp.status_code, 200)

    def test_success_mod_by_student(self):
        data = {'token': '123456', 'course_name': 'Matan', 'course_material_name': 'Lecture 1',
                'course_material_body': 'No info'}
        resp = self.client.post(reverse('manage_course_materials'), data)
        self.assertEqual(resp.status_code, 200)

    def test_success_delete_by_teacher(self):
        data = {'token': '123456', 'course_name': 'Matan', 'course_material_name': 'Lecture 1',
                'course_material_body': ''}
        resp = self.client.post(reverse('manage_course_materials'), data)
        self.assertEqual(resp.status_code, 200)

    def test_bad_course(self):
        data = {'token': '123457', 'course_name': 'Linal', 'course_material_name': 'Lecture 1',
                'course_material_body': 'No info'}
        resp = self.client.post(reverse('manage_course_materials'), data)
        self.assertEqual(resp.status_code, 400)


class AddTrustedIndividualsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        group = Group(group_name="492", department_name="diht", course_number=4)
        group.save()
        student = Student(FIO="Knyazev Alexander", e_mail='foo@example.com', password='password1',
                                          degree='Bachelor', form_of_study='Full-time', learning_base='Budget',
                                          group=group)
        student.save()

        access_token = AccessToken()
        access_token.user = student
        access_token.token = '123456'
        access_token.save()

        teacher = Teacher(FIO="Ivanov Yuri", e_mail='foo2@example.com', password='password2')
        teacher.save()

        access_token2 = AccessToken()
        access_token2.user = teacher
        access_token2.token = '123457'
        access_token2.save()

        course = Course(course_name='Matan', description='---')
        course.groups_of_course.add(group)
        course.course_instructors.add(teacher)
        course.save()

        course2 = Course(course_name='Linal', description='---')
        course2.groups_of_course.add(group)
        course2.save()

    def test_success_case(self):
        data = {'token': '123457', 'course_name': 'Matan', 'trusted_individual_id': 1}
        resp = self.client.post(reverse('add_trusted_individuals'), data)
        self.assertEqual(resp.status_code, 200)

    def test_bad_teacher_access(self):
        data = {'token': '123457', 'course_name': 'Linal', 'trusted_individual_id': 1}
        resp = self.client.post(reverse('add_trusted_individuals'), data)
        self.assertEqual(resp.status_code, 403)

    def test_bad_student_access(self):
        data = {'token': '123456', 'course_name': 'Matan', 'trusted_individual_id': 1}
        resp = self.client.post(reverse('add_trusted_individuals'), data)
        self.assertEqual(resp.status_code, 403)

    def test_bad_request(self):
        data = {'token': '123456', 'course_name': 'Philosophy', 'trusted_individual_id': 1}
        resp = self.client.post(reverse('add_trusted_individuals'), data)
        self.assertEqual(resp.status_code, 400)

    def test_invalid_token(self):
        data = {'token': '123', 'course_name': 'Matan', 'trusted_individual_id': 1}
        resp = self.client.post(reverse('add_trusted_individuals'), data)
        self.assertEqual(resp.status_code, 401)


class ManageCourseTasksTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        teacher = Teacher(FIO="Ivanov Yuri", e_mail='foo2@example.com', password='password2')
        teacher.save()

        access_token = AccessToken()
        access_token.user = teacher
        access_token.token = '123457'
        access_token.save()

        course = Course(course_name='Matan', description='---')
        course.course_instructors.add(teacher)
        course.save()

        course2 = Course(course_name='Linal', description='---')
        course2.save()

        task = Task(task_name="HW 1", course=course, description='---', start=datetime.datetime.now(),
                    end=datetime.datetime.now() + datetime.timedelta(days=7))
        task.save()

    def test_success_add(self):
        data = {'token': '123457', 'course_name': 'Matan', 'task_name': 'HW 2', 'task_body': 'Solve smth',
                'task_start': datetime.datetime.now(), 'task_end': datetime.datetime.now() + datetime.timedelta(days=7)}
        resp = self.client.post(reverse('manage_course_task'), data)
        self.assertEqual(resp.status_code, 200)

    def test_success_mod(self):
        data = {'token': '123457', 'course_name': 'Matan', 'task_name': 'HW1', 'task_body': 'Solve smth',
                'task_start': datetime.datetime.now(), 'task_end': datetime.datetime.now() + datetime.timedelta(days=9)}
        resp = self.client.post(reverse('manage_course_task'), data)
        self.assertEqual(resp.status_code, 200)

    def test_success_delete(self):
        data = {'token': '123457', 'course_name': 'Matan', 'task_name': 'HW1', 'task_body': '',
                'task_start': datetime.datetime.now(), 'task_end': datetime.datetime.now() + datetime.timedelta(days=9)}
        resp = self.client.post(reverse('manage_course_task'), data)
        self.assertEqual(resp.status_code, 200)

    def test_no_teacher_access(self):
        data = {'token': '123457', 'course_name': 'Linal', 'task_name': 'HW2', 'task_body': 'Solve smth',
                'task_start': datetime.datetime.now(), 'task_end': datetime.datetime.now() + datetime.timedelta(days=7)}
        resp = self.client.post(reverse('manage_course_task'), data)
        self.assertEqual(resp.status_code, 403)

    def test_bad_request(self):
        data = {'token': '123457', 'course': 'Linal', 'task_name': 'HW2', 'content': 'Solve'}
        resp = self.client.post(reverse('manage_course_task'), data)
        self.assertEqual(resp.status_code, 400)

    def test_invalid_token(self):
        data = {'token': '123456', 'course_name': 'Linal', 'task_name': 'HW2', 'task_body': ''}
        resp = self.client.post(reverse('manage_course_task'), data)
        self.assertEqual(resp.status_code, 401)


class UploadTaskSolutionTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        group = Group(group_name="492", department_name="diht", course_number=4)
        group.save()
        student = Student(FIO="Knyazev Alexander", e_mail='foo@example.com', password='password1',
                                          degree='Bachelor', form_of_study='Full-time', learning_base='Budget',
                                          group=group)
        student.save()

        access_token = AccessToken()
        access_token.user = student
        access_token.token = '123456'
        access_token.save()

        teacher = Teacher(FIO="Ivanov Yuri", e_mail='foo2@example.com', password='password2')
        teacher.save()

        access_token2 = AccessToken()
        access_token2.user = teacher
        access_token2.token = '123457'
        access_token2.save()

        course = Course(course_name='Matan', description='---')
        course.course_instructors.add(teacher)
        course.groups_of_course.add(group)
        course.save()

        course2 = Course(course_name='Linal', description='---')
        course2.course_instructors.add(teacher)
        course2.save()

        task = Task(task_name="HW 1", course=course, description='---', start=datetime.datetime.now(),
                    end=datetime.datetime.now() + datetime.timedelta(days=7))
        task.save()

        task2 = Task(task_name="HW 1", course=course2, description='---', start=datetime.datetime.now(),
                    end=datetime.datetime.now() + datetime.timedelta(days=7))
        task2.save()

    def test_success_add(self):
        data = {'token': '123456', 'course_name': 'Matan', 'task_id': '1', 'solution_body': 'answer 1'}
        resp = self.client.post(reverse('upload_task_solution'), data)
        self.assertEqual(resp.status_code, 200)

    def test_no_access(self):
        data = {'token': '123456', 'course_name': 'Linal', 'task_id': '1', 'solution_body': 'answer 1'}
        resp = self.client.post(reverse('upload_task_solution'), data)
        self.assertEqual(resp.status_code, 403)

    def test_no_access(self):
        data = {'token': '123456', 'course': 'Linal', 'task': '1', 'solution_body': 'answer 1'}
        resp = self.client.post(reverse('upload_task_solution'), data)
        self.assertEqual(resp.status_code, 400)

    def test_invalid_token(self):
        data = {'token': '123', 'course_name': 'Matan', 'task_id': '1', 'solution_body': 'answer 1'}
        resp = self.client.post(reverse('upload_task_solution'), data)
        self.assertEqual(resp.status_code, 400)


class WatchTaskSolutionTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        group = Group(group_name="492", department_name="diht", course_number=4)
        group.save()
        student = Student(FIO="Knyazev Alexander", e_mail='foo@example.com', password='password1',
                                          degree='Bachelor', form_of_study='Full-time', learning_base='Budget',
                                          group=group)
        student.save()

        group2 = Group(group_name="493", department_name="diht", course_number=4)
        group2.save()
        student2 = Student(FIO="Sidorov Ivan", e_mail='foo3@example.com', password='password3',
                          degree='Bachelor', form_of_study='Full-time', learning_base='Budget',
                          group=group2)
        student2.save()

        access_token = AccessToken()
        access_token.user = student
        access_token.token = '123456'
        access_token.save()

        teacher = Teacher(FIO="Ivanov Yuri", e_mail='foo2@example.com', password='password2')
        teacher.save()

        access_token2 = AccessToken()
        access_token2.user = teacher
        access_token2.token = '123457'
        access_token2.save()

        course = Course(course_name='Matan', description='---')
        course.course_instructors.add(teacher)
        course.groups_of_course.add(group)
        course.save()

        task = Task(task_name="HW 1", course=course, description='---', start=datetime.datetime.now(),
                    end=datetime.datetime.now() + datetime.timedelta(days=7))
        task.save()

    def test_success_case(self):
        data = {'token': '123457', 'task_id': '1'}
        resp = self.client.post(reverse('watch_task_solution'), data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context), 2)

    def test_no_access(self):
        data = {'token': '123456', 'task_id': '1'}
        resp = self.client.post(reverse('watch_task_solution'), data)
        self.assertEqual(resp.status_code, 403)

    def test_bad_request(self):
        data = {'token': '123456', 'course_name': 'Matan', 'task_name': 'HW 1'}
        resp = self.client.post(reverse('watch_task_solution'), data)
        self.assertEqual(resp.status_code, 400)

    def test_invalid_token(self):
        data = {'token': '123', 'task_id': '1'}
        resp = self.client.post(reverse('watch_task_solution'), data)
        self.assertEqual(resp.status_code, 401)