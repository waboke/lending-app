from django.urls import path
from .views import KYCSubmissionView, KYCApproveView

urlpatterns = [
    path('status/', KYCSubmissionView.as_view(), name='kyc-status'),
    path('submit/', KYCSubmissionView.as_view(), name='kyc-submit'),
    path('review/<uuid:user_id>/approve/', KYCApproveView.as_view(), name='kyc-approve'),
]
