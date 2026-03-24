from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import (User, Profile,
                     MilitaryProfile,
                     CivilServantProfile,
                     BusinessProfile,
                     ParamilitaryProfile,
                       KYC, OTP)

#Register user
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'password', 'role']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
#Login
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            email=data['email'],
            password=data['password']
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User is inactive")

        refresh = RefreshToken.for_user(user)

        return {
            "user": user,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }
#Profile Serializers

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['category', 'phone_number', 'address']

class ProfileCreateUpdateSerializer(serializers.Serializer):
    category = serializers.CharField()
    phone_number = serializers.CharField()
    address = serializers.CharField()
    extra = serializers.DictField()

    def validate_category(self, value):
        allowed = ["military", "paramilitary", "civil_servant", "businessman"]
        if value not in allowed:
            raise serializers.ValidationError("Invalid category")
        return value
    #  Cross-field / DB validation
    def validate(self, data):
        user = self.context['request'].user

        if hasattr(user, "profile"):
            if user.profile.category != data.get("category"):
                raise serializers.ValidationError(
                    "Category change not allowed"
                )

        return data
    
    def create(self, validated_data):
        user = self.context['request'].user

        category = validated_data['category']
        extra = validated_data['extra']

        # Create/update base profile
        profile, _ = Profile.objects.update_or_create(
            user=user,
            defaults={
                "category": category,
                "phone_number": validated_data["phone_number"],
                "address": validated_data["address"],
            }
        )

        # Handle category-specific model
        if category == "military":
            MilitaryProfile.objects.update_or_create(
                user=user,
                defaults=extra
            )

        elif category == "paramilitary":
            ParamilitaryProfile.objects.update_or_create(
                user=user,
                defaults=extra
            )

        elif category == "civil_servant":
            CivilServantProfile.objects.update_or_create(
                user=user,
                defaults=extra
            )

        elif category == "businessman":
            BusinessProfile.objects.update_or_create(
                user=user,
                defaults=extra
            )

        return profile
    
        
#Military Serializers
class MilitaryProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilitaryProfile
        exclude = ['user']

#Civil Servant
class CivilServantSerializer(serializers.ModelSerializer):
    class Meta:
        model = CivilServantProfile
        exclude = ['user']
#Bussiness
class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessProfile
        exclude = ['user']

#paramilitary
class ParamilitarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ParamilitaryProfile
        exclude = ['user']

class KYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYC
        fields = '__all__'
        read_only_fields = ['user', 'status']


class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['code']