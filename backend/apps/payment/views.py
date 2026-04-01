from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import generics
from apps.loan.models import Loan
from apps.branch.views import get_user_branch_ids
from .models import PaymentTransaction
from .serializers import PaymentTransactionSerializer
from .services import initiate_payment, apply_successful_payment, save_webhook


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
