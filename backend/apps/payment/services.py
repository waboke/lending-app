import uuid
from decimal import Decimal
from django.db import transaction
from apps.loan.models import LoanStatus
from .models import PaymentTransaction, WebhookEvent, PaymentStatus


def initiate_payment(user, loan, amount, payment_method='bank_transfer'):
    if loan.user_id != user.id:
        raise ValueError('Loan does not belong to user')
    if loan.status not in [LoanStatus.ACTIVE, LoanStatus.OVERDUE]:
        raise ValueError('Loan is not payable')
    reference = f'PAY-{uuid.uuid4().hex[:12].upper()}'
    return PaymentTransaction.objects.create(
        user=user,
        loan=loan,
        reference=reference,
        amount=Decimal(amount),
        payment_method=payment_method,
        status=PaymentStatus.PENDING,
    )


@transaction.atomic
def apply_successful_payment(txn: PaymentTransaction):
    if txn.status == PaymentStatus.SUCCESSFUL:
        return txn
    txn.status = PaymentStatus.SUCCESSFUL
    txn.save(update_fields=['status', 'updated_at'])
    remaining = txn.amount
    loan = txn.loan
    for schedule in loan.repayment_schedules.filter(is_paid=False).order_by('installment_number'):
        installment_remaining = schedule.total_amount - schedule.paid_amount
        if remaining <= 0:
            break
        applied = min(remaining, installment_remaining)
        schedule.paid_amount += applied
        if schedule.paid_amount >= schedule.total_amount:
            schedule.is_paid = True
        schedule.save(update_fields=['paid_amount', 'is_paid', 'updated_at'])
        remaining -= applied
    loan.outstanding_balance = max(Decimal('0'), loan.outstanding_balance - txn.amount)
    if loan.outstanding_balance <= 0:
        loan.status = LoanStatus.CLOSED
    loan.save(update_fields=['outstanding_balance', 'status', 'updated_at'])
    return txn


def save_webhook(provider, event_id, event_type, payload):
    event, _ = WebhookEvent.objects.get_or_create(
        event_id=event_id,
        defaults={'provider': provider, 'event_type': event_type, 'payload': payload}
    )
    return event
