from django.urls import path, include
from .views import RegisterView, LoginView
from .views import (ProfileCreateUpdateView,
                    ProfileDetailView,
                    KYCView, 
                    SendOTPView, 
                    VerifyOTPView)

urlpatterns= [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileCreateUpdateView.as_view()),
    path('profile/detail/', ProfileDetailView.as_view()),
    path('kyc/', KYCView.as_view()),
    path('otp/send/', SendOTPView.as_view()),
    path('otp/verify/', VerifyOTPView.as_view()),
   
]