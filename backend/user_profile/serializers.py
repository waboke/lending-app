from rest_framework import serializers
from .models import ( Profile,
                     MilitaryProfile,
                     CivilServantProfile,
                     BusinessProfile,
                     ParamilitaryProfile
                    )


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

