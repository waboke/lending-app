from rest_framework import serializers


class SendOTPSerializer(serializers.Serializer):
    channel = serializers.ChoiceField(choices=['sms', 'email'])
    purpose = serializers.ChoiceField(choices=['registration', 'login'])


class VerifyOTPSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)
    purpose = serializers.ChoiceField(choices=['registration', 'login'])
