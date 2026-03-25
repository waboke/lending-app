from django.urls import path
from .views import NotificationListView, MarkAsReadView

urlpatterns = [
    path('', NotificationListView.as_view()),
    path('<int:pk>/read/', MarkAsReadView.as_view()),
]