from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/otp/', include('apps.otp.urls')),
    path('api/v1/profile/', include('apps.user_profile.urls')),
    path('api/v1/kyc/', include('apps.kyc.urls')),
    path('api/v1/credit/', include('apps.credit.urls')),
    path('api/v1/', include('apps.loan.urls')),
    path('api/v1/payments/', include('apps.payment.urls')),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
