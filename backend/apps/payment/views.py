from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import generics
from apps.loan.models import Loan
from .models import PaymentTransaction
from .serializers import PaymentTransactionSerializer
from .services import initiate_payment, apply_successful_payment, save_webhook


class PaymentInitiateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        loan = Loan.objects.get(id=request.data['loan'])
        txn = initiate_payment(request.user, loan, request.data['amount'], request.data.get('payment_method', 'bank_transfer'))
        return Response({'reference': txn.reference, 'status': txn.status, 'amount': str(txn.amount)})


class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return PaymentTransaction.objects.filter(user=self.request.user)


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
