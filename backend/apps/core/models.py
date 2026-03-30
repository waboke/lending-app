import uuid
from django.db import models


class TimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel):
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class AuditLog(TimeStampedModel):
    actor = models.CharField(max_length=255, blank=True, null=True)
    action = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=100)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f'{self.action} - {self.entity_type}'
