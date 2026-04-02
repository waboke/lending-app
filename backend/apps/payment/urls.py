from django.urls import path
from .views import PaymentInitiateView, PaymentDetailView, PaymentWebhookView, BankAccountView, AutoDebitSetupView, AutoDebitProcessView

urlpatterns = [
    path('initiate/', PaymentInitiateView.as_view(), name='payment-initiate'),
    path('webhook/', PaymentWebhookView.as_view(), name='payment-webhook'),
    path('<uuid:id>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('bank-account/', BankAccountView.as_view(), name='bank-account'),
    path('auto-debit/', AutoDebitSetupView.as_view(), name='auto-debit-setup'),
    path('auto-debit/process/', AutoDebitProcessView.as_view(), name='auto-debit-process'),
]
