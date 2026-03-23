from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Profile

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(
            username=data['email'],  # important
            password=data['password']
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("Account not verified")

        refresh = RefreshToken.for_user(user)

        return {
            'user': user.email,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()

    def validate(self, data):
        user = User.objects.get(email=data['email'])
        otp = OTP.objects.filter(user=user, code=data['code'], is_verified=False).last()

        if not otp:
            raise serializers.ValidationError("Invalid OTP")

        if otp.is_expired():
            raise serializers.ValidationError("OTP expired")

        otp.is_verified = True
        otp.save()

        user.is_active = True
        user.is_verified = True
        user.save()

        return {"message": "Verified successfully"}

class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        user = User.objects.get(email=data['email'])

        # delete old OTPs
        OTP.objects.filter(user=user, is_verified=False).delete()

        import random
        otp = OTP.objects.create(
            user=user,
            code=str(random.randint(100000, 999999))
        )

        print(f"New OTP: {otp.code}")  # replace with SMS later

        return {"message": "OTP resent"}