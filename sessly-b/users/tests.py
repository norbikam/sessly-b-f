"""
Comprehensive tests for users app.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from datetime import timedelta

from .models import EmailVerification

User = get_user_model()


class UserRegistrationTests(TestCase):
    """Tests for user registration."""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test123!@#',
            'password2': 'Test123!@#',
            'first_name': 'Test',
            'last_name': 'User',
        }
    
    def test_successful_registration(self):
        """Test successful user registration."""
        response = self.client.post(self.register_url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # Verify user was created
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
    
    def test_duplicate_email(self):
        """Test registration with duplicate email."""
        # Create first user
        User.objects.create_user(
            username='existing',
            email='test@example.com',
            password='Test123!@#'
        )
        
        # Try to register with same email
        response = self.client.post(self.register_url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        if 'success' in response.data and not response.data['success']:
            self.assertEqual(response.data['error']['code'], 'EMAIL_ALREADY_EXISTS')
    
    def test_password_mismatch(self):
        """Test registration with mismatched passwords."""
        data = self.valid_data.copy()
        data['password2'] = 'DifferentPassword123!@#'
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_weak_password(self):
        """Test registration with weak password."""
        data = self.valid_data.copy()
        data['password'] = '123'
        data['password2'] = '123'
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTests(TestCase):
    """Tests for user login."""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('token_obtain_pair')
        
        # Create active user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Test123!@#',
            is_active=True
        )
    
    def test_successful_login(self):
        """Test successful login with valid credentials."""
        data = {
            'username': 'testuser',
            'password': 'Test123!@#'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_wrong_password(self):
        """Test login with wrong password."""
        data = {
            'username': 'testuser',
            'password': 'WrongPassword123!@#'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        if 'success' in response.data and not response.data['success']:
            self.assertEqual(response.data['error']['code'], 'INVALID_CREDENTIALS')
    
    def test_nonexistent_user(self):
        """Test login with non-existent username."""
        data = {
            'username': 'nonexistent',
            'password': 'Test123!@#'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class EmailVerificationTests(TestCase):
    """Tests for email verification."""
    
    def setUp(self):
        self.client = APIClient()
        self.verify_url = reverse('verify_email')
        self.resend_url = reverse('resend_verify_email')
        
        # Create inactive user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Test123!@#',
            is_active=False
        )
        
        # Create verification code
        self.verification = EmailVerification.objects.create(
            user=self.user,
            code='123456',
            expires_at=timezone.now() + timedelta(minutes=15)
        )
    
    def test_successful_verification(self):
        """Test successful email verification."""
        data = {
            'email': 'test@example.com',
            'code': '123456'
        }
        
        response = self.client.post(self.verify_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify user is now active
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
    
    def test_invalid_code(self):
        """Test verification with invalid code."""
        data = {
            'email': 'test@example.com',
            'code': '999999'
        }
        
        response = self.client.post(self.verify_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_expired_code(self):
        """Test verification with expired code."""
        # Make the code expired
        self.verification.expires_at = timezone.now() - timedelta(minutes=1)
        self.verification.save()
        
        data = {
            'email': 'test@example.com',
            'code': '123456'
        }
        
        response = self.client.post(self.verify_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ChangePasswordTests(TestCase):
    """Tests for password change."""
    
    def setUp(self):
        self.client = APIClient()
        self.change_password_url = reverse('change_password')
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='OldPassword123!@#',
            is_active=True
        )
        
        # Login to get token
        self.client.force_authenticate(user=self.user)
    
    def test_successful_password_change(self):
        """Test successful password change."""
        data = {
            'old_password': 'OldPassword123!@#',
            'new_password': 'NewPassword123!@#',
            'new_password2': 'NewPassword123!@#'
        }
        
        response = self.client.put(self.change_password_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify new password works
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123!@#'))
    
    def test_wrong_old_password(self):
        """Test password change with wrong old password."""
        data = {
            'old_password': 'WrongPassword123!@#',
            'new_password': 'NewPassword123!@#',
            'new_password2': 'NewPassword123!@#'
        }
        
        response = self.client.put(self.change_password_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        if 'success' in response.data and not response.data['success']:
            self.assertEqual(response.data['error']['code'], 'WRONG_PASSWORD')
    
    def test_password_mismatch(self):
        """Test password change with mismatched new passwords."""
        data = {
            'old_password': 'OldPassword123!@#',
            'new_password': 'NewPassword123!@#',
            'new_password2': 'DifferentPassword123!@#'
        }
        
        response = self.client.put(self.change_password_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutTests(TestCase):
    """Tests for user logout."""
    
    def setUp(self):
        self.client = APIClient()
        self.logout_url = reverse('logout')
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Test123!@#',
            is_active=True
        )
        
        # Get refresh token
        from rest_framework_simplejwt.tokens import RefreshToken
        self.refresh = RefreshToken.for_user(self.user)
        
        self.client.force_authenticate(user=self.user)
    
    def test_successful_logout(self):
        """Test successful logout."""
        data = {
            'refresh': str(self.refresh)
        }
        
        response = self.client.post(self.logout_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

