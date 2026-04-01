from django.db.models import Count, Sum, Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.kyc.models import KYCSubmission, KYCStatus
from apps.loan.models import LoanApplication, Loan, LoanStatus, LoanApplicationStatus
from .models import Branch, BranchStaffAssignment
from .serializers import BranchSerializer, BranchStaffAssignmentSerializer


def get_user_branch_ids(user):
    return list(user.branch_assignments.values_list('branch_id', flat=True))


class BranchListView(generics.ListAPIView):
    queryset = Branch.objects.filter(is_active=True)
    serializer_class = BranchSerializer
    permission_classes = [AllowAny]


class BranchDetailView(generics.RetrieveAPIView):
    queryset = Branch.objects.filter(is_active=True)
    serializer_class = BranchSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'


class MyBranchAssignmentsView(generics.ListAPIView):
    serializer_class = BranchStaffAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BranchStaffAssignment.objects.filter(user=self.request.user).select_related('branch', 'user')


class BranchDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        branch_ids = get_user_branch_ids(user)
        if not branch_ids and not user.is_head_office:
            return Response({'detail': 'No branch assignment found'}, status=404)

        app_qs = LoanApplication.objects.all()
        loan_qs = Loan.objects.all()
        kyc_qs = KYCSubmission.objects.all()
        if not user.is_head_office:
            app_qs = app_qs.filter(branch_id__in=branch_ids)
            loan_qs = loan_qs.filter(branch_id__in=branch_ids)
            kyc_qs = kyc_qs.filter(branch_id__in=branch_ids)

        data = {
            'pending_applications': app_qs.filter(status=LoanApplicationStatus.SUBMITTED).count(),
            'approved_applications': app_qs.filter(status=LoanApplicationStatus.APPROVED).count(),
            'pending_kyc': kyc_qs.filter(status__in=[KYCStatus.PENDING, KYCStatus.UNDER_REVIEW]).count(),
            'approved_kyc': kyc_qs.filter(status=KYCStatus.APPROVED).count(),
            'active_loans': loan_qs.filter(status=LoanStatus.ACTIVE).count(),
            'overdue_loans': loan_qs.filter(status=LoanStatus.OVERDUE).count(),
            'portfolio_outstanding': str(loan_qs.aggregate(total=Sum('outstanding_balance'))['total'] or 0),
            'branches_managed': Branch.objects.filter(id__in=branch_ids).count() if not user.is_head_office else Branch.objects.count(),
        }
        return Response(data)
