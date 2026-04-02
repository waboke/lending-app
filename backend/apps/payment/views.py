from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import generics
from apps.loan.models import Loan
from apps.branch.views import get_user_branch_ids
from .models import PaymentTransaction, BankAccount, AutoDebitSetup
from .serializers import PaymentTransactionSerializer, BankAccountSerializer, AutoDebitSetupSerializer
from .services import initiate_payment, apply_successful_payment, save_webhook, AutoDebitService


class PaymentInitiateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        loan = Loan.objects.get(id=request.data['loan'])
        if request.user.is_branch_staff and loan.branch_id not in get_user_branch_ids(request.user):
            return Response({'detail': 'Cannot initiate payment outside your branch'}, status=403)
        txn = initiate_payment(request.user if request.user == loan.user else loan.user, loan, request.data['amount'], request.data.get('payment_method', 'bank_transfer'))
        return Response({'reference': txn.reference, 'status': txn.status, 'amount': str(txn.amount)})


class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        qs = PaymentTransaction.objects.all()
        if user.is_head_office or user.is_staff:
            return qs
        if user.is_branch_staff:
            return qs.filter(loan__branch_id__in=get_user_branch_ids(user))
        return qs.filter(user=user)


class PaymentWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.data
        event = save_webhook(
            provider=payload.get('provider', 'manual'),
            event_id=payload.get('event_id', payload.get('reference', 'unknown-event')),
            event_type=payload.get('event_type', 'payment.success'),
            payload=payload,
        )
        reference = payload.get('reference')
        txn = PaymentTransaction.objects.filter(reference=reference).first()
        if txn and payload.get('status') == 'successful':
            apply_successful_payment(txn)
        return Response({'status': 'processed'})


class BankAccountView(generics.RetrieveUpdateAPIView):
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return BankAccount.objects.filter(user=self.request.user).first()

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj:
            return Response({'detail': 'Bank account not set up'}, status=404)
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj:
            # Create new bank account
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        else:
            # Update existing
            serializer = self.get_serializer(obj, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class AutoDebitSetupView(generics.RetrieveUpdateAPIView):
    serializer_class = AutoDebitSetupSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return AutoDebitSetup.objects.filter(user=self.request.user).first()

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj:
            return Response({'detail': 'Auto debit not set up'}, status=404)
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # Set up auto debit
        bank_account_data = request.data.get('bank_account')
        max_amount = request.data.get('max_amount_per_debit')
        frequency = request.data.get('frequency', 'monthly')

        if not bank_account_data or not max_amount:
            return Response({'detail': 'Bank account data and max amount are required'}, status=400)

        auto_debit = AutoDebitService.setup_auto_debit(
            request.user, bank_account_data, max_amount, frequency
        )
        serializer = self.get_serializer(auto_debit)
        return Response(serializer.data, status=201)

    def patch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj:
            return Response({'detail': 'Auto debit not set up'}, status=404)

        action = request.data.get('action')
        if action == 'enable':
            result = AutoDebitService.enable_auto_debit(request.user)
        elif action == 'disable':
            result = AutoDebitService.disable_auto_debit(request.user)
        else:
            return Response({'detail': 'Invalid action'}, status=400)

        if result['status'] == 'success':
            obj.refresh_from_db()
            serializer = self.get_serializer(obj)
            return Response(serializer.data)
        else:
            return Response({'detail': result['message']}, status=400)


class AutoDebitProcessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Manually trigger auto debit processing (for testing/admin purposes)
        result = AutoDebitService.process_auto_debit(request.user)
        return Response(result, status=200 if result['status'] in ['success', 'skipped'] else 400)


class PaymentInitiateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        loan = Loan.objects.get(id=request.data['loan'])
        if request.user.is_branch_staff and loan.branch_id not in get_user_branch_ids(request.user):
            return Response({'detail': 'Cannot initiate payment outside your branch'}, status=403)
        txn = initiate_payment(request.user if request.user == loan.user else loan.user, loan, request.data['amount'], request.data.get('payment_method', 'bank_transfer'))
        return Response({'reference': txn.reference, 'status': txn.status, 'amount': str(txn.amount)})


class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        qs = PaymentTransaction.objects.all()
        if user.is_head_office or user.is_staff:
            return qs
        if user.is_branch_staff:
            return qs.filter(loan__branch_id__in=get_user_branch_ids(user))
        return qs.filter(user=user)


class PaymentWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.data
        event = save_webhook(
            provider=payload.get('provider', 'manual'),
            event_id=payload.get('event_id', payload.get('reference', 'unknown-event')),
            event_type=payload.get('event_type', 'payment.success'),
            payload=payload,
        )
        reference = payload.get('reference')
        txn = PaymentTransaction.objects.filter(reference=reference).first()
        if txn:
            apply_successful_payment(txn)
            event.processed = True
            event.save(update_fields=['processed', 'updated_at'])
        return Response({'detail': 'Webhook received', 'processed': event.processed})
