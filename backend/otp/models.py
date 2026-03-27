
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class OTP(models.Model):
    PURPOSE_CHOICES = (
        ("login", "Login"),
        ("kyc", "KYC"),
        ("password_reset", "Password Reset"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES)

    is_used = models.BooleanField(default=False)

    expires_at = models.DateTimeField()
    attempt_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def can_attempt(self):
        return self.attempt_count < 5

    @staticmethod
    def generate_code():
        import random
        return str(random.randint(100000, 999999))

    @classmethod
    def create_otp(cls, user, purpose):
        code = cls.generate_code()
        expires_at = timezone.now() + timedelta(minutes=5)

        return cls.objects.create(
            user=user,
            code=code,
            purpose=purpose,
            expires_at=expires_at
        )