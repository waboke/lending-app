from django.urls import path
from .views import ProfileView, BankAccountListCreateView

urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
    path('bank-accounts/', BankAccountListCreateView.as_view(), name='bank-accounts'),
]
