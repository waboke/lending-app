from django.db import models
from django.conf import settings

# Create your models here.
#profile
CATEGORY_CHOICES = (
    ("military", "Military"),
    ("paramilitary", "Paramilitary"),
    ("civil_servant", "Civil Servant"),
    ("businessman", "Businessman"),
)
class Profile(models.Model):
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)

    phone_number = models.CharField(max_length=20, unique=True)
    address = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.category == "military" and not hasattr(self.user, "militaryprofile"):
            raise ValidationError("Military profile required")

# Military personnel
class MilitaryProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    service_number = models.CharField(max_length=50)
    rank = models.CharField(max_length=50)
    unit = models.CharField(max_length=100)
    years_of_service = models.IntegerField()

#paramilitary
class ParamilitaryProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    agency = models.CharField(max_length=100)
    rank = models.CharField(max_length=50)
    service_id = models.CharField(max_length=50)

#Civil Sercices
class CivilServantProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    ministry = models.CharField(max_length=100)
    grade_level = models.CharField(max_length=20)
    employee_id = models.CharField(max_length=50)
#Bussnessme
class BusinessProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    business_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100)
    annual_revenue = models.DecimalField(max_digits=12, decimal_places=2)