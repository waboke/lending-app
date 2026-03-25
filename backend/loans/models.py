<<<<<<< HEAD
from django.db import models
from django.conf import settings

# Create your models here.
class Loan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()  # months
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    
    status = models.CharField(choices=[
=======
# Create your models here.
from django.db import models
from django.conf import settings


class Loan(models.Model):
    STATUS_CHOICES = [
>>>>>>> rupert_users
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
<<<<<<< HEAD
    ]
    
    created_at = models.DateTimeField(auto_now_add=True)
=======
    ]
    

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loans'
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in months")

    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    reason = models.TextField(blank=True, null=True)  # rejection reason

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.amount} ({self.status})"
>>>>>>> rupert_users
