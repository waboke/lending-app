from django.db import models
import uuid
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
import random
from django.utils import timezone
from datetime import timedelta
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("staff", "Staff"),
        ("borrower", "Borrower"),
    )

    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(max_length=255)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="borrower")

    # Status flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Verification flags
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)

    # Security tracking
    last_login = models.DateTimeField(blank=True, null=True)
    last_password_change = models.DateTimeField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return self.email

    @property
    def is_verified(self):
        return self.is_email_verified and self.is_phone_verified

#profile
CATEGORY_CHOICES = (
    ("military", "Military"),
    ("paramilitary", "Paramilitary"),
    ("civil_servant", "Civil Servant"),
    ("businessman", "Businessman"),
)
#Base Profile
class Profile(models.Model):
    
    user = models.OneToOneField("User", on_delete=models.CASCADE)

    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)

    phone_number = models.CharField(max_length=20, unique=True)
    address = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.category == "military" and not hasattr(self.user, "militaryprofile"):
            raise ValidationError("Military profile required")

# Military personnel
class MilitaryProfile(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE)

    service_number = models.CharField(max_length=50)
    rank = models.CharField(max_length=50)
    unit = models.CharField(max_length=100)
    years_of_service = models.IntegerField()

#paramilitary
class ParamilitaryProfile(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE)

    agency = models.CharField(max_length=100)
    rank = models.CharField(max_length=50)
    service_id = models.CharField(max_length=50)

#Civil Sercices
class CivilServantProfile(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE)

    ministry = models.CharField(max_length=100)
    grade_level = models.CharField(max_length=20)
    employee_id = models.CharField(max_length=50)
#Bussnessme
class BusinessProfile(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE)

    business_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100)
    annual_revenue = models.DecimalField(max_digits=12, decimal_places=2)
#KYC    
class KYC(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("under_review", "Under Review"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    )

    user = models.OneToOneField("User", on_delete=models.CASCADE)

    id_number = models.CharField(max_length=50, unique=True)
    document_type = models.CharField(max_length=50)

    document_image = models.ImageField(upload_to="kyc/")
    selfie_image = models.ImageField(upload_to="kyc/")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    reviewed_by = models.ForeignKey(
        "User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="kyc_reviews"
    )

    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
#OTP  

class OTP(models.Model):
    PURPOSE_CHOICES = (
        ("login", "Login"),
        ("kyc", "KYC"),
        ("password_reset", "Password Reset"),
    )

    user = models.ForeignKey("User", on_delete=models.CASCADE)

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