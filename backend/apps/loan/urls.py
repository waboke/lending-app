from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import LoanProductViewSet, LoanApplicationViewSet, LoanViewSet, LoanApplicationApproveView

router = DefaultRouter()
router.register('loan-products', LoanProductViewSet, basename='loan-product')
router.register('loan-applications', LoanApplicationViewSet, basename='loan-application')
router.register('loans', LoanViewSet, basename='loan')

urlpatterns = [
    path('loan-applications/<uuid:pk>/approve/', LoanApplicationApproveView.as_view(), name='loan-application-approve'),
] + router.urls
