from django.db import models
from django.utils import timezone
#from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin)
from .managers import UserManager
#from user_profile.models import Profile, MilitaryProfile, ParamilitaryProfile, CivilServantProfile, BusinessProfile

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


