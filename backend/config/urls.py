
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="Lending API",
      default_version='v1',
      description="API documentation for lending app",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    # This creates /api/users/...
    path('api/users/', include('users.urls')),
    path('api/loans/', include('loans.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/nortifications/', include('notifications.urls')),
    path('api/credit/', include('credit.urls')),
    path('api/core/', include('core.urls')),
    path('api/kyc/', include('kyc.urls')),
    path('api/otp/', include('otp.urls')),
    #path('docs/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
