from django.urls import path
from .views import CreditEvaluateView, CreditLatestView

urlpatterns = [
    path('evaluate/', CreditEvaluateView.as_view(), name='credit-evaluate'),
    path('latest/', CreditLatestView.as_view(), name='credit-latest'),
]
