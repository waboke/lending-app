from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import LoanProduct, LoanApplication, Loan
from .serializers import LoanProductSerializer, LoanApplicationSerializer, LoanSerializer, RepaymentScheduleSerializer
from .services import get_available_products, submit_application, approve_application, disburse_loan


class LoanProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LoanProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_available_products(self.request.user)


class LoanApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = LoanApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return LoanApplication.objects.all()
        return LoanApplication.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        application = self.get_object()
        submit_application(application)
        return Response({'detail': 'Application submitted'})


class LoanApplicationApproveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not request.user.is_staff:
            return Response({'detail': 'Admin only'}, status=status.HTTP_403_FORBIDDEN)
        application = LoanApplication.objects.get(pk=pk)
        loan = approve_application(application)
        return Response({'loan_id': str(loan.id), 'detail': 'Application approved'})


class LoanViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Loan.objects.all()
        return Loan.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def disburse(self, request, pk=None):
        loan = self.get_object()
        if not request.user.is_staff:
            return Response({'detail': 'Admin only'}, status=status.HTTP_403_FORBIDDEN)
        disburse_loan(loan)
        return Response({'detail': 'Loan disbursed'})

    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        loan = self.get_object()
        serializer = RepaymentScheduleSerializer(loan.repayment_schedules.all(), many=True)
        return Response(serializer.data)
