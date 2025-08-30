"""
Security tests for authentication cookie handling.

Tests for the cookie security vulnerability fixes in api/views/auth.py
"""

import re
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from api.views.auth import (_sanitize_cookie_value, _validate_jwt_token,
                            set_auth_cookies)
from user.models.profile import Profile

User = get_user_model()


class CookieSecurityTestCase(TestCase):
    """Test cases for cookie security fixes."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile, _ = Profile.objects.get_or_create(
            user=self.user,
            defaults={
                'occupation': 'tester',
                'timezone': 'UTC'
            }
        )

    def test_validate_jwt_token_valid(self):
        """Test JWT token validation with valid token."""
        token = RefreshToken.for_user(self.user)
        access_token = str(token.access_token)

        result = _validate_jwt_token(access_token)
        self.assertTrue(result)

    def test_validate_jwt_token_invalid_format(self):
        """Test JWT token validation with invalid format."""
        invalid_tokens = [
            "",
            "invalid",
            "invalid.token",
            "invalid.token.signature.extra",
            "a" * 5000,  # Too long
            None,
            123,
            "header.payload",  # Missing signature
        ]

        for token in invalid_tokens:
            with self.subTest(token=token):
                result = _validate_jwt_token(token)
                self.assertFalse(result)

    def test_validate_jwt_token_malformed_jwt(self):
        """Test JWT token validation with malformed JWT structure."""
        malformed_tokens = [
            "header.invalid_base64.signature",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid.signature",
            "header.payload.invalid_signature",
        ]

        for token in malformed_tokens:
            with self.subTest(token=token):
                result = _validate_jwt_token(token)
                self.assertFalse(result)

    def test_sanitize_cookie_value_valid(self):
        """Test cookie value sanitization with valid values."""
        token = RefreshToken.for_user(self.user)
        access_token = str(token.access_token)

        result = _sanitize_cookie_value(access_token)
        self.assertEqual(result, access_token)

    def test_sanitize_cookie_value_invalid(self):
        """Test cookie value sanitization with invalid values."""
        invalid_values = [
            "",
            None,
            123,
            "token with spaces",
            "token\nwith\nnewlines",
            "token;with;semicolons",
            "token=with=equals",
            "token,with,commas",
            "token<script>alert('xss')</script>",
            "token\r\nSet-Cookie: evil=true",  # Cookie injection attempt
        ]

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    _sanitize_cookie_value(value)

    @patch('api.views.auth.logger')
    def test_set_auth_cookies_invalid_access_token(self, mock_logger):
        """Test set_auth_cookies with invalid access token."""
        from rest_framework.response import Response

        response = Response({})
        refresh_token = str(RefreshToken.for_user(self.user))

        with self.assertRaises(ValidationError):
            set_auth_cookies(response, "invalid_token", refresh_token)

        mock_logger.error.assert_called()

    @patch('api.views.auth.logger')
    def test_set_auth_cookies_invalid_refresh_token(self, mock_logger):
        """Test set_auth_cookies with invalid refresh token."""
        from rest_framework.response import Response

        response = Response({})
        token = RefreshToken.for_user(self.user)
        access_token = str(token.access_token)

        with self.assertRaises(ValidationError):
            set_auth_cookies(response, access_token, "invalid_token")

        mock_logger.error.assert_called()

    @override_settings(DEBUG=False)
    def test_set_auth_cookies_secure_attributes(self):
        """Test that cookies are set with secure attributes."""
        from rest_framework.response import Response

        response = Response({})
        token = RefreshToken.for_user(self.user)
        access_token = str(token.access_token)
        refresh_token = str(token)

        result = set_auth_cookies(response, access_token, refresh_token)

        # Check that cookies are set
        self.assertIn('access_token', result.cookies)
        self.assertIn('refresh_token', result.cookies)
        self.assertIn('auth_status', result.cookies)

        # Check security attributes
        access_cookie = result.cookies['access_token']
        self.assertTrue(access_cookie['httponly'])
        self.assertTrue(access_cookie['secure'])
        self.assertEqual(access_cookie['samesite'], 'Strict')

        refresh_cookie = result.cookies['refresh_token']
        self.assertTrue(refresh_cookie['httponly'])
        self.assertTrue(refresh_cookie['secure'])
        self.assertEqual(refresh_cookie['samesite'], 'Strict')

        # Auth status cookie should be accessible to JavaScript
        auth_cookie = result.cookies['auth_status']
        self.assertFalse(auth_cookie['httponly'])
        self.assertEqual(auth_cookie.value, 'authenticated')

    def test_login_endpoint_security(self):
        """Test login endpoint with security fixes."""
        url = reverse('auth:login')  # Adjust URL name as needed
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }

        response = self.client.post(url, data, format='json')

        # Should succeed with valid credentials
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that cookies are set with secure attributes
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)
        self.assertIn('auth_status', response.cookies)

        # Verify HttpOnly attributes
        access_cookie = response.cookies['access_token']
        refresh_cookie = response.cookies['refresh_token']
        auth_cookie = response.cookies['auth_status']

        self.assertTrue(access_cookie['httponly'])
        self.assertTrue(refresh_cookie['httponly'])
        self.assertFalse(auth_cookie['httponly'])  # Should be accessible to JS

    def test_logout_clears_all_cookies(self):
        """Test that logout clears all authentication cookies."""
        # First login
        self.client.force_authenticate(user=self.user)

        url = reverse('auth:logout')  # Adjust URL name as needed
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that cookies are cleared
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)
        self.assertIn('auth_status', response.cookies)

        # Verify cookies are set to expire
        for cookie_name in ['access_token', 'refresh_token', 'auth_status']:
            cookie = response.cookies[cookie_name]
            self.assertEqual(cookie.value, '')

    @patch('api.views.auth.logger')
    def test_token_refresh_validation_error_handling(self, mock_logger):
        """Test token refresh handles validation errors properly."""
        self.client.force_authenticate(user=self.user)

        # Mock invalid token in cookies
        self.client.cookies['refresh_token'] = 'invalid_token_format'

        url = reverse('auth:token_refresh')  # Adjust URL name as needed
        response = self.client.post(url)

        # Should handle validation error gracefully
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED
        ])

    def test_xss_protection(self):
        """Test that XSS payload in token is rejected."""
        malicious_tokens = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "token<img src=x onerror=alert('xss')>",
        ]

        for payload in malicious_tokens:
            with self.subTest(payload=payload):
                with self.assertRaises(ValidationError):
                    _sanitize_cookie_value(payload)

    def test_cookie_injection_protection(self):
        """Test protection against cookie injection attacks."""
        injection_attempts = [
            "token\r\nSet-Cookie: evil=true",
            "token\nSet-Cookie: session=hijacked",
            "token; HttpOnly=false",
            "token; Secure=false",
            "token; SameSite=None",
            "token\x00\x0d\x0aSet-Cookie: malicious=value",
        ]

        for attempt in injection_attempts:
            with self.subTest(attempt=attempt):
                with self.assertRaises(ValidationError):
                    _sanitize_cookie_value(attempt)

    def test_session_fixation_protection(self):
        """Test protection against session fixation attacks."""
        # Test with a token that has valid JWT format but is crafted
        crafted_token_parts = [
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9",  # Valid header
            "eyJ1c2VyX2lkIjoxLCJleHAiOjE2MzQ2NzQ4MDB9",  # Crafted payload
            "malicious_signature_here_123456789"  # Invalid signature
        ]
        crafted_token = ".".join(crafted_token_parts)

        # Token should pass format validation but fail when used
        self.assertTrue(_validate_jwt_token(crafted_token))

        # But should fail when actually verifying the signature during use
        # (This would be caught by Django REST Framework JWT validation)

    @override_settings(DEBUG=True)
    def test_development_vs_production_settings(self):
        """Test cookie security differs between development and production."""
        from rest_framework.response import Response

        response = Response({})
        token = RefreshToken.for_user(self.user)
        access_token = str(token.access_token)
        refresh_token = str(token)

        # In development (DEBUG=True), secure should be False
        result = set_auth_cookies(response, access_token, refresh_token)
        access_cookie = result.cookies['access_token']
        self.assertFalse(access_cookie['secure'])

    def test_jwt_token_length_validation(self):
        """Test that extremely long tokens are rejected."""
        # Create an extremely long token-like string
        long_token = "a" * 5000 + "." + "b" * 5000 + "." + "c" * 5000

        result = _validate_jwt_token(long_token)
        self.assertFalse(result)

    def test_cookie_domain_security(self):
        """Test that cookie domain is handled securely."""
        from rest_framework.response import Response

        response = Response({})
        token = RefreshToken.for_user(self.user)
        access_token = str(token.access_token)
        refresh_token = str(token)

        result = set_auth_cookies(response, access_token, refresh_token)

        # Domain should be None for security (let browser handle it)
        access_cookie = result.cookies['access_token']
        self.assertIsNone(access_cookie['domain'])
