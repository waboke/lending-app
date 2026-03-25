from django.urls import path
from .views import CreditScoreView

urlpatterns = [
    path('score/', CreditScoreView.as_view()),
]