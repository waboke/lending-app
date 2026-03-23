from django.db import models
from django.contrib.auth.models import  AbstractUser , PermissionsMixin
from django.db import models
from .managers import UserManager



# Create your models here.
ROLE_CHOICES = (
    ('customer', 'Customer'),
    ('admin', 'Admin'),
    ('staff', 'Staff'),
)
    
class User(AbstractUser):

    # 🔹 Role Choices
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        STAFF = 'staff', 'Staff'
        BORROWER = 'borrower', 'Borrower'

    # 🔹 Override email to be unique (used for login)
    email = models.EmailField(unique=True)

    # 🔹 Extra fields
    phone_number = models.CharField(max_length=15, unique=True)

    # (Already exists in AbstractUser, but we keep for clarity/control)
    first_name = models.CharField(max_length=50, blank=True )
    last_name = models.CharField(max_length=50,blank=True )

    # 🔹 Role field
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.BORROWER
    )

    # 🔹 Custom flags
    is_verified = models.BooleanField(default=False)

    # 🔹 Manager
    objects = UserManager()

    # 🔹 Use email instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']

    # 🔹 Helper methods
    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def is_admin(self):
        return self.role == self.Role.ADMIN

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField()

    bvn = models.CharField(max_length=11, unique=True)  # Nigeria-specific
   
    national_id = models.CharField(max_length=50, blank=True)

    is_kyc_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email
    

class KYC(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    id_type = models.CharField(max_length=50)
    id_number = models.CharField(max_length=100)

    document_image = models.ImageField(upload_to='kyc/')
    selfie_image = models.ImageField(upload_to='kyc/')

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('verified', 'Verified'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)