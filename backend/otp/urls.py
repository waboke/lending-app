from django.urls import path, include
from .views import SendOTPView, VerifyOTPView

urlpatterns= [
    
    path('otp/send/', SendOTPView.as_view()),
    path('otp/verify/', VerifyOTPView.as_view()),
   
]