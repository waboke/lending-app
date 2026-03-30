from rest_framework import serializers
from .models import CreditAssessment


class CreditAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditAssessment
        fields = '__all__'
