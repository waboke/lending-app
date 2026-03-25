from django.db import models
from django.conf import settings

class CreditScore(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.IntegerField()
    category = models.CharField(max_length=50)
    last_updated = models.DateTimeField(auto_now=True)