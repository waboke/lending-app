from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.branch.views import get_user_branch_ids
from .models import KYCSubmission, KYCStatus
from .serializers import KYCSubmissionSerializer
from .services import NINVerificationService, BVNVerificationService


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


class NINVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_profile = request.user.profile
        nin = request.data.get('nin')

        if not nin:
            return Response({'detail': 'NIN is required'}, status=status.HTTP_400_BAD_REQUEST)

        user_profile.nin = nin
        user_profile.nin_verification_status = 'pending'
        user_profile.save(update_fields=['nin', 'nin_verification_status', 'updated_at'])

        result = NINVerificationService.verify_nin(nin, user_profile)

        return Response(result, status=status.HTTP_200_OK if result['status'] == 'success' else status.HTTP_400_BAD_REQUEST)


class BVNVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_profile = request.user.profile
        bvn = request.data.get('bvn')

        if not bvn:
            return Response({'detail': 'BVN is required'}, status=status.HTTP_400_BAD_REQUEST)

        user_profile.bvn = bvn
        user_profile.bvn_verification_status = 'pending'
        user_profile.save(update_fields=['bvn', 'bvn_verification_status', 'updated_at'])

        result = BVNVerificationService.verify_bvn(bvn, user_profile)

        return Response(result, status=status.HTTP_200_OK if result['status'] == 'success' else status.HTTP_400_BAD_REQUEST)


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
