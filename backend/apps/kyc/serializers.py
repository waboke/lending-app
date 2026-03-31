from rest_framework import serializers
from .models import KYCSubmission


class KYCSubmissionSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = KYCSubmission
        fields = '__all__'
        read_only_fields = ['user', 'status', 'rejection_reason', 'branch']
