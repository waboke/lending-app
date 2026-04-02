import requests
from django.conf import settings
from apps.user_profile.models import Profile, VerificationStatus


class NINVerificationService:
    """Service for verifying Nigerian National Identification Number (NIN)"""

    API_BASE_URL = "https://api.nimc.gov.ng/api/v1"  # Placeholder - replace with actual NIMC API

    @staticmethod
    def verify_nin(nin: str, user_profile: Profile) -> dict:
        """
        Verify NIN with NIMC API
        Returns verification result
        """
        try:
            # This is a placeholder implementation
            # In production, integrate with actual NIMC API
            api_key = getattr(settings, 'NIMC_API_KEY', 'test-api-key')
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'nin': nin,
                'first_name': user_profile.first_name,
                'last_name': user_profile.last_name,
                'date_of_birth': user_profile.date_of_birth.isoformat()
            }

            response = requests.post(
                f"{NINVerificationService.API_BASE_URL}/verify",
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'verified':
                    user_profile.nin_verification_status = VerificationStatus.VERIFIED
                    user_profile.save(update_fields=['nin_verification_status', 'updated_at'])
                    return {
                        'status': 'success',
                        'message': 'NIN verified successfully',
                        'data': data
                    }
                else:
                    user_profile.nin_verification_status = VerificationStatus.FAILED
                    user_profile.save(update_fields=['nin_verification_status', 'updated_at'])
                    return {
                        'status': 'failed',
                        'message': 'NIN verification failed',
                        'data': data
                    }
            else:
                user_profile.nin_verification_status = VerificationStatus.FAILED
                user_profile.save(update_fields=['nin_verification_status', 'updated_at'])
                return {
                    'status': 'error',
                    'message': f'API error: {response.status_code}',
                    'data': response.text
                }

        except requests.RequestException as e:
            user_profile.nin_verification_status = VerificationStatus.FAILED
            user_profile.save(update_fields=['nin_verification_status', 'updated_at'])
            return {
                'status': 'error',
                'message': f'Request failed: {str(e)}'
            }


class BVNVerificationService:
    """Service for verifying Bank Verification Number (BVN)"""

    API_BASE_URL = "https://api.cbn.gov.ng/bvn"  # Placeholder - replace with actual CBN API

    @staticmethod
    def verify_bvn(bvn: str, user_profile: Profile) -> dict:
        """
        Verify BVN with CBN API
        Returns verification result
        """
        try:
            # This is a placeholder implementation
            # In production, integrate with actual CBN BVN API
            api_key = getattr(settings, 'CBN_API_KEY', 'test-api-key')
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'bvn': bvn,
                'first_name': user_profile.first_name,
                'last_name': user_profile.last_name,
                'date_of_birth': user_profile.date_of_birth.isoformat()
            }

            response = requests.post(
                f"{BVNVerificationService.API_BASE_URL}/verify",
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'verified':
                    user_profile.bvn_verification_status = VerificationStatus.VERIFIED
                    user_profile.save(update_fields=['bvn_verification_status', 'updated_at'])
                    return {
                        'status': 'success',
                        'message': 'BVN verified successfully',
                        'data': data
                    }
                else:
                    user_profile.bvn_verification_status = VerificationStatus.FAILED
                    user_profile.save(update_fields=['bvn_verification_status', 'updated_at'])
                    return {
                        'status': 'failed',
                        'message': 'BVN verification failed',
                        'data': data
                    }
            else:
                user_profile.bvn_verification_status = VerificationStatus.FAILED
                user_profile.save(update_fields=['bvn_verification_status', 'updated_at'])
                return {
                    'status': 'error',
                    'message': f'API error: {response.status_code}',
                    'data': response.text
                }

        except requests.RequestException as e:
            user_profile.bvn_verification_status = VerificationStatus.FAILED
            user_profile.save(update_fields=['bvn_verification_status', 'updated_at'])
            return {
                'status': 'error',
                'message': f'Request failed: {str(e)}'
            }