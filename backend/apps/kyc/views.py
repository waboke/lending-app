from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import KYCSubmission, KYCStatus
from .serializers import KYCSubmissionSerializer


class KYCSubmissionView(generics.RetrieveUpdateAPIView):
    serializer_class = KYCSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return KYCSubmission.objects.filter(user=self.request.user).first()

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj:
            obj = KYCSubmission.objects.create(user=request.user, id_type='national_id', id_number='')
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj:
            obj = KYCSubmission.objects.create(user=request.user, id_type='national_id', id_number='')
        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, status=KYCStatus.UNDER_REVIEW)
        return Response(serializer.data)


class KYCApproveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if not request.user.is_staff:
            return Response({'detail': 'Admin only'}, status=status.HTTP_403_FORBIDDEN)
        submission = KYCSubmission.objects.get(user_id=user_id)
        submission.status = KYCStatus.APPROVED
        submission.rejection_reason = ''
        submission.save(update_fields=['status', 'rejection_reason', 'updated_at'])
        return Response({'detail': 'KYC approved'})
