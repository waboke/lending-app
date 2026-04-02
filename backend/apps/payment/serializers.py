from rest_framework import serializers
from .models import PaymentTransaction, AutoDebitSetup
from apps.user_profile.models import BankAccount


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = '__all__'
        read_only_fields = ['user', 'status']


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['id', 'account_name', 'account_number', 'bank_code', 'bank_name', 'is_salary_account', 'is_verified', 'created_at', 'updated_at']
        read_only_fields = ['user', 'is_verified', 'created_at', 'updated_at']


class AutoDebitSetupSerializer(serializers.ModelSerializer):
    bank_account = BankAccountSerializer(read_only=True)

    class Meta:
        model = AutoDebitSetup
        fields = ['id', 'bank_account', 'status', 'max_amount_per_debit', 'frequency', 'next_debit_date', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
