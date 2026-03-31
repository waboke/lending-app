from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from apps.core.models import BaseModel


class UserRole(models.TextChoices):
    SUPER_ADMIN = 'super_admin', 'Super Admin'
    HEAD_OFFICE_ADMIN = 'head_office_admin', 'Head Office Admin'
    BRANCH_MANAGER = 'branch_manager', 'Branch Manager'
    LOAN_OFFICER = 'loan_officer', 'Loan Officer'
    CREDIT_OFFICER = 'credit_officer', 'Credit Officer'
    KYC_OFFICER = 'kyc_officer', 'KYC Officer'
    CASHIER = 'cashier', 'Cashier'
    CUSTOMER = 'customer', 'Customer'


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email,  **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', UserRole.CUSTOMER)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.SUPER_ADMIN)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser, BaseModel):
    username = None
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=50, choices=UserRole.choices, default=UserRole.CUSTOMER)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    objects = UserManager()

    @property
    def is_head_office(self):
        return self.role in [UserRole.SUPER_ADMIN, UserRole.HEAD_OFFICE_ADMIN]

    @property
    def is_branch_staff(self):
        return self.role in [
            UserRole.BRANCH_MANAGER,
            UserRole.LOAN_OFFICER,
            UserRole.CREDIT_OFFICER,
            UserRole.KYC_OFFICER,
            UserRole.CASHIER,
        ]

    def __str__(self):
        return self.email
