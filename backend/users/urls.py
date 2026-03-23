from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, MeView, UserViewSet, ProfileViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/me/', MeView.as_view(), name='me'),
    path('', include(router.urls)),
]