from rest_framework import serializers
from .models import KYCSubmission


class KYCSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCSubmission
        fields = '__all__'
        read_only_fields = ['user', 'status', 'rejection_reason']
