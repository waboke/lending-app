from django.urls import path, include
from .views import ProfileCreateUpdateView, ProfileDetailView

urlpatterns= [
   
    path('profile/', ProfileCreateUpdateView.as_view()),
    path('profile/detail/', ProfileDetailView.as_view()),
    
   
]