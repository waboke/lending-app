from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, OTP, Profile
import random


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def create_otp(sender, instance, created, **kwargs):
    if created:
        OTP.objects.create(
            user=instance,
            code=str(random.randint(100000, 999999))
        )
