from django.urls import path
from .views import BranchListView, BranchDetailView, MyBranchAssignmentsView, BranchDashboardView

urlpatterns = [
    path('', BranchListView.as_view(), name='branch-list'),
    path('<uuid:id>/', BranchDetailView.as_view(), name='branch-detail'),
    path('staff/my-assignments/', MyBranchAssignmentsView.as_view(), name='branch-my-assignments'),
    path('staff/dashboard/', BranchDashboardView.as_view(), name='branch-dashboard'),
]
