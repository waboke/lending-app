from django.shortcuts import render
from rest_framework import generics, viewsets, permissions
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import (RegisterSerializer,LoginSerializer,
                          ProfileCreateUpdateSerializer, MilitaryProfileSerializer,
                          ParamilitarySerializer, CivilServantSerializer,
                          BusinessSerializer, KYCSerializer) 
from .models import (User, Profile, MilitaryProfile,
                      CivilServantProfile, BusinessProfile,
                     ParamilitaryProfile, KYC, OTP)
from .permissions import IsAdmin
from .models import OTP
from django.utils.timezone import now
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

class ProfileCreateUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProfileCreateUpdateSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Profile saved successfully"})

#Profile Detail
class ProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = user.profile

        data = {
            "category": profile.category,
            "phone_number": profile.phone_number,
            "address": profile.address,
        }

        # Attach category-specific data
        if profile.category == "military":
            data["extra"] = MilitaryProfileSerializer(user.militaryprofile).data

        elif profile.category == "paramilitary":
            data["extra"] = ParamilitarySerializer(user.paramilitaryprofile).data

        elif profile.category == "civil_servant":
            data["extra"] = CivilServantSerializer(user.civilservantprofile).data

        elif profile.category == "businessman":
            data["extra"] = BusinessSerializer(user.businessprofile).data

        return Response(data)

    
class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data)

        return Response(serializer.errors, status=400)

class ResendOTPView(APIView):
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data)

        return Response(serializer.errors, status=400)

#KYC
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


class SendOTPView(APIView):
    def post(self, request):
        user = request.user
        code = OTP.generate_otp()

        OTP.objects.create(user=user, code=code)

        # TODO: integrate SMS/email service
        print(f"OTP for {user.email}: {code}")

        return Response({"message": "OTP sent"})
    

#VerifyOPT
class VerifyOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("code")
        purpose = request.data.get("purpose")

        otp = OTP.objects.filter(
            user=request.user,
            code=code,
            purpose=purpose,
            is_used=False
        ).last()

        if not otp:
            return Response({"error": "Invalid OTP"}, status=400)

        if otp.is_expired():
            return Response({"error": "OTP expired"}, status=400)

        if not otp.can_attempt():
            return Response({"error": "Too many attempts"}, status=400)

        otp.is_used = True
        otp.save()

        return Response({"message": "OTP verified"})

def is_expired(self):
    return now() > self.created_at + timedelta(minutes=5)