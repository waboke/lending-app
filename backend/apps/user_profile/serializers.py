from rest_framework import serializers
from .models import Profile, BankAccount, CustomerCategory, ResidencyStatus


class ProfileSerializer(serializers.ModelSerializer):
    home_branch_name = serializers.CharField(source='home_branch.name', read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ['user']

    def validate(self, attrs):
        category = attrs.get('customer_category', getattr(self.instance, 'customer_category', None))
        residency = attrs.get('residency_status', getattr(self.instance, 'residency_status', None))
        home_branch = attrs.get('home_branch', getattr(self.instance, 'home_branch', None))

        if category in [
            CustomerCategory.MILITARY,
            CustomerCategory.PARAMILITARY,
            CustomerCategory.CIVIL_SERVANT,
            CustomerCategory.PRIVATE_SECTOR,
        ]:
            if not attrs.get('employer_name') and not getattr(self.instance, 'employer_name', None):
                raise serializers.ValidationError({'employer_name': 'Required for salaried users'})
            if not attrs.get('monthly_income') and not getattr(self.instance, 'monthly_income', None):
                raise serializers.ValidationError({'monthly_income': 'Required for salaried users'})

        if category == CustomerCategory.BUSINESSMAN:
            if not attrs.get('business_name') and not getattr(self.instance, 'business_name', None):
                raise serializers.ValidationError({'business_name': 'Required for businessmen'})
            if not attrs.get('average_monthly_turnover') and not getattr(self.instance, 'average_monthly_turnover', None):
                raise serializers.ValidationError({'average_monthly_turnover': 'Required for businessmen'})

        if residency == ResidencyStatus.RESIDENT_NIGERIA:
            if not attrs.get('state_of_residence') and not getattr(self.instance, 'state_of_residence', None):
                raise serializers.ValidationError({'state_of_residence': 'Required'})
            if not attrs.get('bvn') and not getattr(self.instance, 'bvn', None):
                raise serializers.ValidationError({'bvn': 'BVN required for local users'})

        if residency == ResidencyStatus.DIASPORA:
            if not attrs.get('foreign_address') and not getattr(self.instance, 'foreign_address', None):
                raise serializers.ValidationError({'foreign_address': 'Required'})
            if not home_branch:
                raise serializers.ValidationError({'home_branch': 'Diaspora users must select a servicing branch in Nigeria'})

        if not home_branch:
            raise serializers.ValidationError({'home_branch': 'Home branch is required'})

        return attrs


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'
        read_only_fields = ['user']
