from django.db import models
from django.conf import settings


class CreditScore(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    score = models.IntegerField(default=0)
    category = models.CharField(max_length=50, blank=True)

    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.score}"