from django.shortcuts import render
from .serializers import KYCSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

# Create your views here.

from rest_framework import generics
class KYCView(generics.CreateAPIView):
    serializer_class = KYCSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

#KYCStatus
class KYCStatusView(generics.RetrieveAPIView):
    serializer_class = KYCSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.kyc

#OTP

