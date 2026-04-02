from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import LoanApplication, Loan
from .serializers import LoanApplicationSerializer, LoanSerializer


def _broadcast_update(event_type, instance, user_group=None, branch_group=None, admin_group=False):
    channel_layer = get_channel_layer()
    payload = None

    if isinstance(instance, LoanApplication):
        payload = LoanApplicationSerializer(instance).data
    elif isinstance(instance, Loan):
        payload = LoanSerializer(instance).data

    group_names = set()
    if user_group:
        group_names.add(user_group)
    if branch_group:
        group_names.add(branch_group)
    if admin_group:
        group_names.add('loans_admins')

    for group in group_names:
        async_to_sync(channel_layer.group_send)(
            group,
            {
                'type': 'loan_update',
                'event': event_type,
                'payload': payload,
            }
        )


@receiver(post_save, sender=LoanApplication)
def loan_application_saved(sender, instance, created, **kwargs):
    event = 'loan_application.created' if created else 'loan_application.updated'
    user_group = f'user_{instance.user_id}' if instance.user_id else None
    branch_group = f'branch_{instance.branch_id}' if instance.branch_id else None
    _broadcast_update(event, instance, user_group=user_group, branch_group=branch_group)


@receiver(post_save, sender=Loan)
def loan_saved(sender, instance, created, **kwargs):
    event = 'loan.created' if created else 'loan.updated'
    user_group = f'user_{instance.user_id}' if instance.user_id else None
    branch_group = f'branch_{instance.branch_id}' if instance.branch_id else None
    _broadcast_update(event, instance, user_group=user_group, branch_group=branch_group)
