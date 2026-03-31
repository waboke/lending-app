from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import SendOTPSerializer, VerifyOTPSerializer
from .services import send_otp, verify_otp


class SendOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = send_otp(request.user, serializer.validated_data['channel'], serializer.validated_data['purpose'])
        return Response({'detail': 'OTP generated', 'otp_for_dev': otp.code}, status=status.HTTP_201_CREATED)


class VerifyOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = verify_otp(request.user, serializer.validated_data['code'], serializer.validated_data['purpose'])
        return Response({'detail': 'OTP verified', 'verified_at': otp.verified_at})
