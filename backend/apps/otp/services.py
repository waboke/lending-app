import random
from datetime import timedelta
from django.utils import timezone
from .models import OTPChallenge


def send_otp(user, channel, purpose):
    code = f"{random.randint(100000, 999999)}"
    otp = OTPChallenge.objects.create(
        user=user,
        channel=channel,
        purpose=purpose,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=10),
    )
    return otp


def verify_otp(user, code, purpose):
    otp = OTPChallenge.objects.filter(user=user, purpose=purpose, verified_at__isnull=True).order_by('-created_at').first()
    if not otp:
        raise ValueError('No active OTP found')
    if otp.expires_at < timezone.now():
        raise ValueError('OTP expired')
    otp.attempts += 1
    if otp.code != code:
        otp.save(update_fields=['attempts', 'updated_at'])
        raise ValueError('Invalid OTP code')
    otp.verified_at = timezone.now()
    otp.save(update_fields=['attempts', 'verified_at', 'updated_at'])
    if otp.channel == 'sms':
        user.is_phone_verified = True
    if otp.channel == 'email':
        user.is_email_verified = True
    user.save(update_fields=['is_phone_verified', 'is_email_verified', 'updated_at'])
    return otp
