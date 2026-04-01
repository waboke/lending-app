from django.conf import settings
from django.db import models
from apps.core.models import BaseModel
from apps.branch.models import Branch


class KYCStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    UNDER_REVIEW = 'under_review', 'Under Review'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class KYCSubmission(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='kyc_submission')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='kyc_submissions')
    id_type = models.CharField(max_length=50)
    id_number = models.CharField(max_length=100)
    document_front = models.FileField(upload_to='kyc/documents/', blank=True, null=True)
    document_back = models.FileField(upload_to='kyc/documents/', blank=True, null=True)
    selfie = models.FileField(upload_to='kyc/selfies/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=KYCStatus.choices, default=KYCStatus.PENDING)
    rejection_reason = models.TextField(blank=True, null=True)
