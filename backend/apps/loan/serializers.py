from rest_framework import serializers
from .models import LoanProduct, LoanApplication, Loan, RepaymentSchedule


class LoanProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanProduct
        fields = '__all__'


class LoanApplicationSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = LoanApplication
        fields = '__all__'
        read_only_fields = ['user', 'status', 'review_note', 'branch', 'branch_decision', 'branch_decision_note', 'reviewed_by']


class LoanSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = Loan
        fields = '__all__'


class RepaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepaymentSchedule
        fields = '__all__'
