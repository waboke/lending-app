from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class KYC(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("under_review", "Under Review"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    id_number = models.CharField(max_length=50, unique=True)
    document_type = models.CharField(max_length=50)

    document_image = models.ImageField(upload_to="kyc/")
    selfie_image = models.ImageField(upload_to="kyc/")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    reviewed_by = models.ForeignKey(
       settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="kyc_reviews"
    )

    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
#OTP  