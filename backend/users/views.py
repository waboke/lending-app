from django.shortcuts import render
from rest_framework import generics, viewsets, permissions
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import (RegisterSerializer, LoginSerializer)
from .models import (User)
from .permissions import IsAdmin
from otp.models import OTP
from kyc.models import KYC
from datetime import timedelta


#Register user
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully",
                "email": user.email
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#Login



class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data

            return Response({
                "access": data["access"],
                "refresh": data["refresh"],
                "email": data["user"].email,
                "role": data["user"].role
            })

        return Response(serializer.errors, status=400)
#update Profile

