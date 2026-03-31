from django.conf import settings
from django.db import models
from apps.core.models import BaseModel


class OTPPurpose(models.TextChoices):
    REGISTRATION = 'registration', 'Registration'
    LOGIN = 'login', 'Login'


class OTPChannel(models.TextChoices):
    SMS = 'sms', 'SMS'
    EMAIL = 'email', 'Email'


class OTPChallenge(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='otp_challenges')
    channel = models.CharField(max_length=10, choices=OTPChannel.choices)
    purpose = models.CharField(max_length=30, choices=OTPPurpose.choices)
    code = models.CharField(max_length=10)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(blank=True, null=True)
    attempts = models.PositiveIntegerField(default=0)

    @property
    def is_verified(self):
        return self.verified_at is not None
