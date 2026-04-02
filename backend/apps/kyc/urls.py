from django.urls import path
from .views import KYCSubmissionView, KYCApproveView, NINVerificationView, BVNVerificationView

urlpatterns = [
    path('status/', KYCSubmissionView.as_view(), name='kyc-status'),
    path('submit/', KYCSubmissionView.as_view(), name='kyc-submit'),
    path('review/<uuid:user_id>/approve/', KYCApproveView.as_view(), name='kyc-approve'),
    path('verify/nin/', NINVerificationView.as_view(), name='nin-verify'),
    path('verify/bvn/', BVNVerificationView.as_view(), name='bvn-verify'),
]
