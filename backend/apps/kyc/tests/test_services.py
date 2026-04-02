from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date
from apps.user_profile.models import Profile, VerificationStatus
from ..services import NINVerificationService, BVNVerificationService


User = get_user_model()


class NINVerificationServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            date_of_birth=date(1990, 1, 1)
        )

    @patch('apps.kyc.services.requests.post')
    def test_verify_nin_success(self, mock_post):
        """Test successful NIN verification"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'verified', 'data': {'name': 'John Doe'}}
        mock_post.return_value = mock_response

        result = NINVerificationService.verify_nin('12345678901', self.profile)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['message'], 'NIN verified successfully')
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.nin_verification_status, VerificationStatus.VERIFIED)

    @patch('apps.kyc.services.requests.post')
    def test_verify_nin_failure(self, mock_post):
        """Test failed NIN verification"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'not_verified', 'message': 'NIN not found'}
        mock_post.return_value = mock_response

        result = NINVerificationService.verify_nin('12345678901', self.profile)

        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['message'], 'NIN verification failed')
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.nin_verification_status, VerificationStatus.FAILED)

    @patch('apps.kyc.services.requests.post')
    def test_verify_nin_api_error(self, mock_post):
        """Test NIN verification API error"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_post.return_value = mock_response

        result = NINVerificationService.verify_nin('12345678901', self.profile)

        self.assertEqual(result['status'], 'error')
        self.assertIn('API error: 500', result['message'])
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.nin_verification_status, VerificationStatus.FAILED)

    @patch('apps.kyc.services.requests.post')
    def test_verify_nin_request_exception(self, mock_post):
        """Test NIN verification request exception"""
        mock_post.side_effect = Exception('Connection timeout')

        result = NINVerificationService.verify_nin('12345678901', self.profile)

        self.assertEqual(result['status'], 'error')
        self.assertIn('Request failed', result['message'])
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.nin_verification_status, VerificationStatus.FAILED)


class BVNVerificationServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            date_of_birth=date(1990, 1, 1)
        )

    @patch('apps.kyc.services.requests.post')
    def test_verify_bvn_success(self, mock_post):
        """Test successful BVN verification"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'verified', 'data': {'name': 'John Doe'}}
        mock_post.return_value = mock_response

        result = BVNVerificationService.verify_bvn('22345678901', self.profile)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['message'], 'BVN verified successfully')
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bvn_verification_status, VerificationStatus.VERIFIED)

    @patch('apps.kyc.services.requests.post')
    def test_verify_bvn_failure(self, mock_post):
        """Test failed BVN verification"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'not_verified', 'message': 'BVN not found'}
        mock_post.return_value = mock_response

        result = BVNVerificationService.verify_bvn('22345678901', self.profile)

        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['message'], 'BVN verification failed')
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bvn_verification_status, VerificationStatus.FAILED)