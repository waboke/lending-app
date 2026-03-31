from django.contrib import admin
from .models import PaymentTransaction, WebhookEvent

admin.site.register(PaymentTransaction)
admin.site.register(WebhookEvent)
