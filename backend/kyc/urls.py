from django.urls import path, include
from .views import KYCView

urlpatterns= [
   
    path('kyc/', KYCView.as_view()),
   
   
]