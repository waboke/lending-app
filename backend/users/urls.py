from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, MeView, UserViewSet, ProfileViewSet,VerifyOTPView,ResendOTPView, LoginView
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/me/', MeView.as_view(), name='me'),
    path('login/', LoginView.as_view()),
    path('verify-otp/', VerifyOTPView.as_view()),
    path('resend-otp/', ResendOTPView.as_view()),

    
]