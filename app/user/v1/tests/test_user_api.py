from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from helpers.cache_adapter import CacheAdapter
from user.v1.constants import OTP_PREFIX


REGISTER_URL = reverse('user:register-user')
LOGIN_URL = reverse('user:login-user')
GENERATE_OTP_URL = reverse('user:generate-otp')
REFRESH_TOKEN_URL = reverse('user:refresh-token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def create_default_user():
    return get_user_model().objects.create_user(
        email="test@gmail.com",
        password="TestPassword$87",
        name="Test User",
        mobile_number="1234567890"
    )


def set_otp(mobile_number='1234567890', otp='123456'):
    obj = CacheAdapter()
    obj.set(OTP_PREFIX + mobile_number, otp, 120)


def get_otp(mobile_number='1234567890'):
    obj = CacheAdapter()
    return obj.get(OTP_PREFIX + mobile_number)


class PublicUserAPITest(TestCase):
    """
    Tests the user APIs (public)
    """

    def setup(self):
        self.client = APIClient()

    def test_register_user_success(self):
        """
        Tests if the user has been created correctly
        using the register user API
        """
        payload = {
            "email": "test@gmail.com",
            "password": "TestPassword$87",
            "confirm_password": "TestPassword$87",
            "name": "Test User",
            "mobile_number": "1234567890"
        }

        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        does_user_exist = get_user_model().objects.filter(
            email="test@gmail.com"
        ).exists()
        self.assertTrue(does_user_exist)

    def test_register_user_empty_payload(self):
        """
        Tests if the API returns error with no payload
        """
        res = self.client.post(REGISTER_URL, {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_wrong_payload1(self):
        """
        Tests if we get 400 on wrong payload - 1
        """
        payload = {
            "email": "test",
            "password": "1234",
            "confirm_password": "1234",
            "mobile_number": "123"
        }

        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', res.data)

    def test_register_user_wrong_payload2(self):
        """
        Test if we get 400 on wrong payload - 2
        """
        payload = {
            "email": "test",
            "password": "1234",
            "confirm_password": "1234",
            "mobile_number": "123",
            "name": "Test"
        }

        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', res.data)
        self.assertIn('password', res.data)
        self.assertIn('mobile_number', res.data)

    def test_register_user_wrong_payload3(self):
        """
        Test if we get 400 on wrong payload - 3
        """
        payload = {
            "email": "test@test.com",
            "password": "Test$1234",
            "confirm_password": "1234",
            "mobile_number": "1234567890",
            "name": "test"
        }

        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', res.data)

    def test_login_user_success_using_password(self):
        """
        Test if the user is logged in succesfully and
        has recieved the tokens - using email/password
        """
        create_default_user()

        payload = {
            "email": "test@gmail.com",
            "password": "TestPassword$87"
        }

        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_login_user_success_using_otp(self):
        """
        Test if the user is logged in successfully and
        has received the tokens - using mobile_number/otp
        """
        create_default_user()

        payload = {
            "mobile_number": "1234567890",
            "otp": "123456"
        }

        set_otp()

        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_login_user_empty_payload(self):
        """
        Test if we get 400 on empty payload
        """
        res = self.client.post(LOGIN_URL, {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', res.data)

    def test_login_user_wrong_payload1(self):
        """
        Test if API returns 400 when passed email id and OTP
        """
        create_default_user()

        payload = {
            "email": "test@gmail.com",
            "otp": "123456"
        }

        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', res.data)

    def test_login_user_wrong_payload2(self):
        """
        Test if API returns 400 when passed mobile_number and passwor
        """
        create_default_user()

        payload = {
            'mobile_number': '1234567890',
            'password': 'TestPassword$87'
        }

        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('otp', res.data)

    def test_login_user_non_existent_user1(self):
        """
        Test if API returns 404 when non existent user
        is login
        """
        payload = {
            'email': 'test@gmail.com',
            'password': 'TestPassword$87'
        }

        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_login_user_non_existent_user2(self):
        """
        Test if API returns 404 when non existent user
        is login
        """
        payload = {
            'mobile_number': '1234567890',
            'otp': '123456'
        }

        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_login_user_wrong_password(self):
        """
        Test if the user is bit logged in when given wrong password
        """
        create_default_user()

        payload = {
            "email": "test@gmail.com",
            "password": "TestPassword$87556"
        }

        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_wrong_otp(self):
        """
        Test if the user is bit logged in when given wrong otp
        """
        create_default_user()

        payload = {
            'mobile_number': '1234567890',
            'otp': '1234567'
        }

        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_generate_otp_success(self):
        """
        Test if the OTP is generated successfully for the user
        """
        create_default_user()

        payload = {
            'mobile_number': '1234567890'
        }

        res = self.client.post(GENERATE_OTP_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        otp = get_otp()
        self.assertIsNotNone(otp)

    def test_generate_otp_non_existent_user(self):
        """
        Test if the OTP is not generated for non existent user
        """
        payload = {
            'mobile_number': '1234567898'
        }

        res = self.client.post(GENERATE_OTP_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        otp = get_otp(payload['mobile_number'])
        self.assertIsNone(otp)

    def test_refersh_token_success(self):
        """
        Test if the API returns a success
        """
        create_default_user()

        login_payload = {
            "email": "test@gmail.com",
            "password": "TestPassword$87"
        }

        login_res = self.client.post(LOGIN_URL, login_payload)

        refresh_token = login_res.data['refresh']

        refresh_payload = {
            'refresh': refresh_token
        }

        refersh_res = self.client.post(REFRESH_TOKEN_URL, refresh_payload)
        self.assertEqual(refersh_res.status_code, status.HTTP_200_OK)
        self.assertIn('access', refersh_res.data)
        self.assertIn('refresh', refersh_res.data)
