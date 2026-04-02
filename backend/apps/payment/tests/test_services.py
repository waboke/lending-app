from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
from apps.loan.models import Loan, LoanStatus
from apps.payment.models import AutoDebitSetup, AutoDebit
from apps.user_profile.models import BankAccount
from ..services import AutoDebitService


User = get_user_model()


class AutoDebitServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.bank_account = BankAccount.objects.create(
            user=self.user,
            account_name='John Doe',
            account_number='0123456789',
            bank_code='001',
            bank_name='Test Bank',
            is_salary_account=True,
            is_verified=True
        )

    def test_setup_auto_debit_new_account(self):
        """Test setting up auto debit with new bank account"""
        bank_data = {
            'account_name': 'Jane Doe',
            'account_number': '0987654321',
            'bank_code': '002',
            'bank_name': 'Another Bank'
        }

        auto_debit = AutoDebitService.setup_auto_debit(
            self.user, bank_data, Decimal('50000'), 'monthly'
        )

        self.assertEqual(auto_debit.status, AutoDebit.DISABLED)
        self.assertEqual(auto_debit.max_amount_per_debit, Decimal('50000'))
        self.assertEqual(auto_debit.frequency, 'monthly')

        # Check that bank account was created
        bank_account = BankAccount.objects.get(user=self.user, account_number='0987654321')
        self.assertEqual(bank_account.account_name, 'Jane Doe')
        self.assertTrue(bank_account.is_salary_account)

    def test_setup_auto_debit_existing_account(self):
        """Test setting up auto debit with existing bank account"""
        bank_data = {
            'account_name': 'Updated Name',
            'account_number': '0123456789',  # Existing account
            'bank_code': '001',
            'bank_name': 'Updated Bank'
        }

        auto_debit = AutoDebitService.setup_auto_debit(
            self.user, bank_data, Decimal('75000'), 'weekly'
        )

        self.assertEqual(auto_debit.status, AutoDebit.DISABLED)
        self.assertEqual(auto_debit.max_amount_per_debit, Decimal('75000'))
        self.assertEqual(auto_debit.frequency, 'weekly')

        # Check that existing bank account was updated
        self.bank_account.refresh_from_db()
        self.assertEqual(self.bank_account.account_name, 'Updated Name')
        self.assertEqual(self.bank_account.bank_name, 'Updated Bank')

    def test_enable_auto_debit(self):
        """Test enabling auto debit"""
        AutoDebitSetup.objects.create(
            user=self.user,
            bank_account=self.bank_account,
            status=AutoDebit.DISABLED,
            max_amount_per_debit=Decimal('50000'),
            frequency='monthly'
        )

        result = AutoDebitService.enable_auto_debit(self.user)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['message'], 'Auto debit enabled')

        auto_debit = AutoDebitSetup.objects.get(user=self.user)
        self.assertEqual(auto_debit.status, AutoDebit.ENABLED)
        self.assertIsNotNone(auto_debit.next_debit_date)

    def test_enable_auto_debit_no_setup(self):
        """Test enabling auto debit when not set up"""
        result = AutoDebitService.enable_auto_debit(self.user)

        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['message'], 'Auto debit not set up')

    def test_disable_auto_debit(self):
        """Test disabling auto debit"""
        AutoDebitSetup.objects.create(
            user=self.user,
            bank_account=self.bank_account,
            status=AutoDebit.ENABLED,
            max_amount_per_debit=Decimal('50000'),
            frequency='monthly',
            next_debit_date=date.today()
        )

        result = AutoDebitService.disable_auto_debit(self.user)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['message'], 'Auto debit disabled')

        auto_debit = AutoDebitSetup.objects.get(user=self.user)
        self.assertEqual(auto_debit.status, AutoDebit.DISABLED)
        self.assertIsNone(auto_debit.next_debit_date)

    @patch('apps.payment.services.AutoDebitService._perform_bank_debit')
    def test_process_auto_debit_success(self, mock_perform_debit):
        """Test successful auto debit processing"""
        mock_perform_debit.return_value = True

        # Create a loan
        loan = Loan.objects.create(
            user=self.user,
            amount=Decimal('100000'),
            outstanding_balance=Decimal('50000'),
            status=LoanStatus.ACTIVE
        )

        # Create repayment schedule
        from apps.loan.models import RepaymentSchedule
        RepaymentSchedule.objects.create(
            loan=loan,
            installment_number=1,
            total_amount=Decimal('25000'),
            paid_amount=Decimal('0'),
            due_date=date.today(),
            is_paid=False
        )

        # Setup auto debit
        auto_debit = AutoDebitSetup.objects.create(
            user=self.user,
            bank_account=self.bank_account,
            status=AutoDebit.ENABLED,
            max_amount_per_debit=Decimal('30000'),
            frequency='monthly',
            next_debit_date=date.today()
        )

        result = AutoDebitService.process_auto_debit(self.user)

        self.assertEqual(result['status'], 'success')
        self.assertIn('Auto debit of 25000 processed successfully', result['message'])

        # Check that payment was created and applied
        from apps.payment.models import PaymentTransaction
        payment = PaymentTransaction.objects.get(user=self.user, loan=loan)
        self.assertEqual(payment.amount, Decimal('25000'))
        self.assertEqual(payment.status, 'successful')

        # Check loan balance updated
        loan.refresh_from_db()
        self.assertEqual(loan.outstanding_balance, Decimal('25000'))

    def test_process_auto_debit_not_due(self):
        """Test auto debit processing when not due"""
        AutoDebitSetup.objects.create(
            user=self.user,
            bank_account=self.bank_account,
            status=AutoDebit.ENABLED,
            max_amount_per_debit=Decimal('50000'),
            frequency='monthly',
            next_debit_date=date.today() + timedelta(days=1)  # Tomorrow
        )

        result = AutoDebitService.process_auto_debit(self.user)

        self.assertEqual(result['status'], 'skipped')
        self.assertEqual(result['message'], 'Not due for debit yet')

    def test_process_auto_debit_no_active_loans(self):
        """Test auto debit processing when no active loans"""
        AutoDebitSetup.objects.create(
            user=self.user,
            bank_account=self.bank_account,
            status=AutoDebit.ENABLED,
            max_amount_per_debit=Decimal('50000'),
            frequency='monthly',
            next_debit_date=date.today()
        )

        result = AutoDebitService.process_auto_debit(self.user)

        self.assertEqual(result['status'], 'skipped')
        self.assertEqual(result['message'], 'No active loans')

    def test_calculate_next_debit_date_monthly(self):
        """Test calculating next debit date for monthly frequency"""
        today = date.today()
        next_date = AutoDebitService._calculate_next_debit_date('monthly')

        # Should be same day next month
        expected = today.replace(day=1) + timedelta(days=32)
        expected = expected.replace(day=min(today.day, (expected.replace(day=1) + timedelta(days=31)).day))

        self.assertEqual(next_date, expected)

    def test_calculate_next_debit_date_weekly(self):
        """Test calculating next debit date for weekly frequency"""
        today = date.today()
        next_date = AutoDebitService._calculate_next_debit_date('weekly')

        expected = today + timedelta(days=7)
        self.assertEqual(next_date, expected)