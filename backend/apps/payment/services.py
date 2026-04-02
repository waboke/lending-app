import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from apps.loan.models import LoanStatus
from .models import PaymentTransaction, WebhookEvent, PaymentStatus, AutoDebitSetup, AutoDebit
from apps.user_profile.models import BankAccount


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
        provider=provider,
        event_id=event_id,
        defaults={
            'event_type': event_type,
            'payload': payload
        }
    )
    return event


class AutoDebitService:
    """Service for handling automatic debits from salary accounts"""

    @staticmethod
    def setup_auto_debit(user, bank_account_data: dict, max_amount: Decimal, frequency: str = 'monthly'):
        """Set up auto debit for a user"""
        bank_account, created = BankAccount.objects.get_or_create(
            user=user,
            defaults={
                'account_name': bank_account_data['account_name'],
                'account_number': bank_account_data['account_number'],
                'bank_code': bank_account_data['bank_code'],
                'bank_name': bank_account_data['bank_name'],
                'is_salary_account': True,
                'is_verified': False
            }
        )

        if not created:
            # Update existing account
            bank_account.account_name = bank_account_data['account_name']
            bank_account.account_number = bank_account_data['account_number']
            bank_account.bank_code = bank_account_data['bank_code']
            bank_account.bank_name = bank_account_data['bank_name']
            bank_account.is_salary_account = True
            bank_account.save()

        auto_debit, created = AutoDebitSetup.objects.get_or_create(
            user=user,
            defaults={
                'bank_account': bank_account,
                'status': AutoDebit.DISABLED,
                'max_amount_per_debit': max_amount,
                'frequency': frequency,
                'next_debit_date': None
            }
        )

        if not created:
            auto_debit.bank_account = bank_account
            auto_debit.max_amount_per_debit = max_amount
            auto_debit.frequency = frequency
            auto_debit.save()

        return auto_debit

    @staticmethod
    def enable_auto_debit(user):
        """Enable auto debit for a user"""
        try:
            auto_debit = AutoDebitSetup.objects.get(user=user)
            auto_debit.status = AutoDebit.ENABLED
            auto_debit.next_debit_date = AutoDebitService._calculate_next_debit_date(auto_debit.frequency)
            auto_debit.save()
            return {'status': 'success', 'message': 'Auto debit enabled'}
        except AutoDebitSetup.DoesNotExist:
            return {'status': 'error', 'message': 'Auto debit not set up'}

    @staticmethod
    def disable_auto_debit(user):
        """Disable auto debit for a user"""
        try:
            auto_debit = AutoDebitSetup.objects.get(user=user)
            auto_debit.status = AutoDebit.DISABLED
            auto_debit.next_debit_date = None
            auto_debit.save()
            return {'status': 'success', 'message': 'Auto debit disabled'}
        except AutoDebitSetup.DoesNotExist:
            return {'status': 'error', 'message': 'Auto debit not set up'}

    @staticmethod
    def process_auto_debit(user):
        """Process automatic debit for a user"""
        try:
            auto_debit = AutoDebitSetup.objects.get(user=user, status=AutoDebit.ENABLED)
            if not auto_debit.next_debit_date or auto_debit.next_debit_date > timezone.now().date():
                return {'status': 'skipped', 'message': 'Not due for debit yet'}

            # Find active loans for the user
            active_loans = user.loans.filter(status__in=[LoanStatus.ACTIVE, LoanStatus.OVERDUE])
            if not active_loans.exists():
                return {'status': 'skipped', 'message': 'No active loans'}

            total_due = Decimal('0')
            for loan in active_loans:
                # Calculate next installment amount
                next_schedule = loan.repayment_schedules.filter(is_paid=False).first()
                if next_schedule:
                    total_due += next_schedule.total_amount - next_schedule.paid_amount

            if total_due <= 0:
                return {'status': 'skipped', 'message': 'No outstanding payments'}

            debit_amount = min(total_due, auto_debit.max_amount_per_debit)

            # Here you would integrate with payment gateway for actual debit
            # For now, we'll simulate the debit
            success = AutoDebitService._perform_bank_debit(auto_debit.bank_account, debit_amount)

            if success:
                # Create payment transactions for each loan
                remaining_amount = debit_amount
                for loan in active_loans:
                    if remaining_amount <= 0:
                        break
                    next_schedule = loan.repayment_schedules.filter(is_paid=False).first()
                    if next_schedule:
                        installment_due = next_schedule.total_amount - next_schedule.paid_amount
                        amount_to_apply = min(remaining_amount, installment_due)

                        txn = initiate_payment(user, loan, amount_to_apply, 'auto_debit')
                        apply_successful_payment(txn)

                        remaining_amount -= amount_to_apply

                # Update next debit date
                auto_debit.next_debit_date = AutoDebitService._calculate_next_debit_date(auto_debit.frequency)
                auto_debit.save()

                return {'status': 'success', 'message': f'Auto debit of {debit_amount} processed successfully'}
            else:
                return {'status': 'failed', 'message': 'Bank debit failed'}

        except AutoDebitSetup.DoesNotExist:
            return {'status': 'error', 'message': 'Auto debit not set up'}

    @staticmethod
    def _calculate_next_debit_date(frequency: str) -> datetime.date:
        """Calculate the next debit date based on frequency"""
        now = timezone.now().date()
        if frequency == 'monthly':
            # Debit on the same day next month
            next_month = now.replace(day=1) + timedelta(days=32)
            return next_month.replace(day=min(now.day, (next_month.replace(day=1) + timedelta(days=31)).day))
        elif frequency == 'weekly':
            return now + timedelta(days=7)
        else:
            # Default to monthly
            next_month = now.replace(day=1) + timedelta(days=32)
            return next_month.replace(day=min(now.day, (next_month.replace(day=1) + timedelta(days=31)).day))

    @staticmethod
    def _perform_bank_debit(bank_account: BankAccount, amount: Decimal) -> bool:
        """Perform actual bank debit - integrate with payment gateway"""
        # This is a placeholder for payment gateway integration
        # In production, integrate with Flutterwave, Paystack, or bank APIs
        try:
            # Simulate API call to debit account
            # response = requests.post('payment_gateway_api/debit', ...)
            # return response.status_code == 200
            return True  # Simulate success for now
        except Exception:
            return False


def save_webhook(provider, event_id, event_type, payload):
    event, _ = WebhookEvent.objects.get_or_create(
        provider=provider,
        event_id=event_id,
        defaults={
            'event_type': event_type,
            'payload': payload
        }
    )
    return event
