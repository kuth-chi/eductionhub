from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

class TokenTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_token_creation(self):
        response = self.client.post(reverse('token_view'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.json())
