from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient


REGISTER_URL = reverse('user:register-user')


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
        does_user_exist = get_user_model().objects.filter(email="test@gmail.com").exists()
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
