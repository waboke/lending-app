from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.branch.views import get_user_branch_ids
from .models import LoanProduct, LoanApplication, Loan
from .serializers import LoanProductSerializer, LoanApplicationSerializer, LoanSerializer, RepaymentScheduleSerializer
from .services import get_available_products, submit_application, approve_application, disburse_loan, recommend_application


def _filter_branch_queryset(queryset, user):
    if user.is_staff or user.is_head_office:
        return queryset
    if user.is_branch_staff:
        return queryset.filter(branch_id__in=get_user_branch_ids(user))
    return queryset.filter(user=user)


class LoanProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LoanProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_available_products(self.request.user)


class LoanApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = LoanApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _filter_branch_queryset(LoanApplication.objects.select_related('branch', 'product', 'user'), self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, branch=getattr(self.request.user.profile, 'home_branch', None))

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        application = self.get_object()
        if application.user != request.user and not request.user.is_head_office:
            return Response({'detail': 'Only the owner can submit this application'}, status=status.HTTP_403_FORBIDDEN)
        submit_application(application)
        return Response({'detail': 'Application submitted'})

    @action(detail=True, methods=['post'])
    def recommend(self, request, pk=None):
        application = self.get_object()
        if not (request.user.is_branch_staff or request.user.is_head_office or request.user.is_staff):
            return Response({'detail': 'Branch staff only'}, status=status.HTTP_403_FORBIDDEN)
        recommended = bool(request.data.get('recommended', True))
        note = request.data.get('note', '')
        recommend_application(application, request.user, recommended, note)
        return Response({'detail': 'Application recommendation saved'})


class LoanApplicationApproveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not (request.user.is_head_office or request.user.is_staff or request.user.role in ['branch_manager', 'credit_officer']):
            return Response({'detail': 'Approval access denied'}, status=status.HTTP_403_FORBIDDEN)
        application = LoanApplication.objects.get(pk=pk)
        if request.user.is_branch_staff and not request.user.is_head_office:
            branch_ids = get_user_branch_ids(request.user)
            if application.branch_id not in branch_ids:
                return Response({'detail': 'Cannot approve outside your branch'}, status=status.HTTP_403_FORBIDDEN)
        loan = approve_application(application, reviewer=request.user)
        return Response({'loan_id': str(loan.id), 'detail': 'Application approved'})


class LoanViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _filter_branch_queryset(Loan.objects.select_related('branch', 'application', 'user'), self.request.user)

    @action(detail=True, methods=['post'])
    def disburse(self, request, pk=None):
        loan = self.get_object()
        if not (request.user.is_head_office or request.user.is_staff or request.user.role in ['branch_manager', 'cashier']):
            return Response({'detail': 'Admin or cashier only'}, status=status.HTTP_403_FORBIDDEN)
        disburse_loan(loan)
        return Response({'detail': 'Loan disbursed'})

    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        loan = self.get_object()
        serializer = RepaymentScheduleSerializer(loan.repayment_schedules.all(), many=True)
        return Response(serializer.data)
