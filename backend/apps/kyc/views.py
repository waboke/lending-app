from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.branch.views import get_user_branch_ids
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
            branch = getattr(getattr(request.user, 'profile', None), 'home_branch', None)
            obj = KYCSubmission.objects.create(user=request.user, branch=branch, id_type='national_id', id_number='')
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj:
            branch = getattr(getattr(request.user, 'profile', None), 'home_branch', None)
            obj = KYCSubmission.objects.create(user=request.user, branch=branch, id_type='national_id', id_number='')
        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, branch=getattr(getattr(request.user, 'profile', None), 'home_branch', None), status=KYCStatus.UNDER_REVIEW)
        return Response(serializer.data)


class KYCApproveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if not (request.user.is_head_office or request.user.is_branch_staff or request.user.is_staff):
            return Response({'detail': 'Admin only'}, status=status.HTTP_403_FORBIDDEN)
        submission = KYCSubmission.objects.get(user_id=user_id)
        if request.user.is_branch_staff and not request.user.is_head_office:
            branch_ids = get_user_branch_ids(request.user)
            if submission.branch_id not in branch_ids:
                return Response({'detail': 'Cannot review KYC outside your branch'}, status=status.HTTP_403_FORBIDDEN)
        submission.status = KYCStatus.APPROVED
        submission.rejection_reason = ''
        submission.save(update_fields=['status', 'rejection_reason', 'updated_at'])
        return Response({'detail': 'KYC approved'})
