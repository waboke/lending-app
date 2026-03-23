from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (RegisterView, 
                    MeView, 
                    UserViewSet, 
                    ProfileViewSet,
                    VerifyOTPView,
                    ResendOTPView,
                      LoginView)
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', MeView.as_view(), name='me'),
    path('login/', LoginView.as_view(), name="login"),
    path('verify-otp/', VerifyOTPView.as_view(), name="verify-otp"),
    path('resend-otp/', ResendOTPView.as_view(), name="resend-otp"),
    path('login/', LoginView.as_view(), name='login'),
   

    
]