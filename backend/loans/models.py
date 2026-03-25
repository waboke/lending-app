from django.db import models
from django.conf import settings

# Create your models here.
class Loan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()  # months
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    
    status = models.CharField(choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
    ])
    
    created_at = models.DateTimeField(auto_now_add=True)