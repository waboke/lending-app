from rest_framework import serializers
from .models import Loan


class LoanApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['id', 'amount', 'duration']

    def create(self, validated_data):
        user = self.context['request'].user
        return Loan.objects.create(user=user, **validated_data)


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'
        read_only_fields = ['status', 'user']