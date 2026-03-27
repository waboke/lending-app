from django.shortcuts import render
from .serializers import OTPSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import OTP
from datetime import timedelta
from django.utils.timezone import now

# Create your views here.

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