from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import User


# Create your tests here.


class UserTests(APITestCase):

    def test_register_user(self):
        url = reverse('register')
        data = {
            "email": "test@test.com",
            "full_name": "Test User",
            "password": "password123",
            "role": "borrower"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

    def test_login_user(self):
        User.objects.create_user(
            email="test@test.com",
            full_name="Test User",
            password="password123"
        )

        url = reverse('login')
        response = self.client.post(url, {
            "email": "test@test.com",
            "password": "password123"
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)