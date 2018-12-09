from django.test import TestCase
from django.urls import reverse
from ..models import *


class AuthTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(e_mail="username@aaa", password="password1")
        user.save()

    def test_success_auth(self):
        data = {'email': 'foo@example.com', 'password': 'password1'}
        resp = self.client.post(reverse('auth'), data)
        self.assertEqual(resp.status_code, 200)

    def test_bad_password(self):
        data = {'email': 'foo@example.com', 'password': 'password2'}
        resp = self.client.post(reverse('auth'), data)
        self.assertEqual(resp.status_code, 406)

    def test_no_user(self):
        data = {'email': 'foo1@example.com', 'password': 'password2'}
        resp = self.client.post(reverse('auth'), data)
        self.assertEqual(resp.status_code, 404)

    def test_bad_request(self):
        data = {'EMAIL': 'foo@example.com', 'password': 'password1'}
        resp = self.client.post(reverse('auth'), data)
        self.assertEqual(resp.status_code, 400)


class RegistrationTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(FIO="Knyazev Alexander")
        user.save()

    def test_success_registration(self):
        user = User.objects.get(id=1)
        code = user.verification_code

        data = {'verification_code': code, 'email': 'foo@example.com', 'password': 'password1'}
        resp = self.client.post(reverse('registration'), data)
        self.assertEqual(resp.status_code, 201)

    def test_bad_verification_code(self):
        user = User.objects.get(id=1)
        code = user.verification_code

        data = {'verification_code': code, 'email': 'foo@example.com', 'password': 'password1'}
        resp = self.client.post(reverse('registration'), data)
        self.assertEqual(resp.status_code, 404)

    def test_bad_request(self):
        user = User.objects.get(id=1)
        code = user.verification_code

        data = {'verification_code': code, 'email': 'foo@example.com'}
        resp = self.client.post(reverse('registration'), data)
        self.assertEqual(resp.status_code, 400)

    def test_bad_email(self):
        user = User.objects.get(id=1)
        code = user.verification_code

        data = {'verification_code': code, 'email': 'foo@example.com', 'password': 'password1'}
        resp = self.client.post(reverse('registration'), data)
        self.assertEqual(resp.status_code, 403)
        self.assertTrue('answer' in resp)
        self.assertEqual(resp['answer'], "Bad e-mail")

    def test_bad_password(self):
        user = User.objects.get(id=1)
        code = user.verification_code

        data = {'verification_code': code, 'email': 'foo@example.com', 'password': '1234'}
        resp = self.client.post(reverse('registration'), data)
        self.assertEqual(resp.status_code, 403)


class MyProfileWatchTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(FIO="Knyazev Alexander", email='foo@example.com', password='password1')
        user.save()
        access_token = AccessToken()
        access_token.user = user
        access_token.token = '123456'
        access_token.save()

    def test_success_case(self):
        data = {'token': '123456'}
        resp = self.client.post(reverse('get_my_profile'), data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('FIO' in resp)
        self.assertEqual(resp['FIO'], 'Knyazev Alexander')

    def test_invalid_token(self):
        data = {'token': '12345678'}
        resp = self.client.post(reverse('get_my_profile'), data)
        self.assertEqual(resp.status_code, 401)


class MyProfileEditTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(FIO="Knyazev Alexander", email='foo@example.com', password='password1')
        user.save()
        access_token = AccessToken()
        access_token.user = user
        access_token.token = '123456'
        access_token.save()

    def test_success_case(self):
        data = {'token': '123456', 'link_to_profile':["https://vk.com/example"], 'phone_number': '+79671219023',
                'person_info': 'I am student', 'hometown': 'Moscow', 'password': 'password2',
                'old_password': 'password1'}
        resp = self.client.post(reverse('edit_my_profile'), data)
        self.assertEqual(resp.status_code, 200)

    def test_invalid_token(self):
        data = {'token': '12345678', 'link_to_profile':["https://vk.com/example"], 'phone_number': '+79671219023',
                'person_info': 'I am student', 'hometown': 'Moscow'}
        resp = self.client.post(reverse('edit_my_profile'), data)
        self.assertEqual(resp.status_code, 401)

    def test_invalid_profile_link(self):
        data = {'token': '12345678', 'link_to_profile':["vk.com/example"], 'phone_number': '+79671219023',
                'person_info': 'I am student', 'hometown': 'Moscow'}
        resp = self.client.post(reverse('edit_my_profile'), data)
        self.assertEqual(resp.status_code, 400)

    def test_invalid_phone_number(self):
        data = {'token': '12345678', 'link_to_profile':["vk.com/example"], 'phone_number': '89671219023',
                'person_info': 'I am student', 'hometown': 'Moscow'}
        resp = self.client.post(reverse('edit_my_profile'), data)
        self.assertEqual(resp.status_code, 400)

    def test_not_editable_field(self):
        data = {'token': '12345678', 'fio': 'Knyazev Aleksandr', 'link_to_profile':["vk.com/example"], 'phone_number': '89671219023',
                'person_info': 'I am student', 'hometown': 'Moscow'}
        resp = self.client.post(reverse('edit_my_profile'), data)
        self.assertEqual(resp.status_code, 400)

    def test_failed_password_change(self):
        data = {'token': '12345678', 'password': 'password2'}
        resp = self.client.post(reverse('edit_my_profile'), data)
        self.assertEqual(resp.status_code, 400)

    def test_failed_password_change2(self):
        data = {'token': '12345678', 'password': 'password2', 'old_password': 'password0'}
        resp = self.client.post(reverse('edit_my_profile'), data)
        self.assertEqual(resp.status_code, 400)

