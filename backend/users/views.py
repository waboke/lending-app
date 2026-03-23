from django.shortcuts import render
from rest_framework import generics, viewsets, permissions
from rest_framework.response import Response
from .models import User, Profile
from .serializers import RegisterSerializer, UserSerializer, ProfileSerializer
from .permissions import IsAdmin

# Register
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


# Current User
class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


# Users (Admin only)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


# Profile
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
