
from django.urls import path
from .views import ApplyLoanView, UserLoansView, LoanDetailView, UpdateLoanStatusView

urlpatterns = [
    path('', UserLoansView.as_view()),
    path('apply/', ApplyLoanView.as_view()),
    path('<int:pk>/', LoanDetailView.as_view()),
    path('<int:pk>/status/', UpdateLoanStatusView.as_view()),
]