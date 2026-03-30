from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Profile, BankAccount
from .serializers import ProfileSerializer, BankAccountSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(
            user=self.request.user,
            defaults={
                'customer_category': 'civil_servant',
                'residency_status': 'resident_nigeria',
                'first_name': self.request.user.email.split('@')[0],
                'last_name': 'User',
                'date_of_birth': '1990-01-01',
                'state_of_residence': 'Lagos',
                'bvn': '00000000000',
                'monthly_income': '100000.00',
                'employer_name': 'Unknown',
            }
        )
        return profile


class BankAccountListCreateView(generics.ListCreateAPIView):
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
