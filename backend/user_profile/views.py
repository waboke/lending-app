from django.shortcuts import render
from .serializers import (ProfileCreateUpdateSerializer, MilitaryProfileSerializer, ParamilitarySerializer, CivilServantSerializer, BusinessSerializer)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# Create your views here.
class ProfileCreateUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProfileCreateUpdateSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Profile saved successfully"})

#Profile Detail
class ProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = user.profile

        data = {
            "category": profile.category,
            "phone_number": profile.phone_number,
            "address": profile.address,
        }

        # Attach category-specific data
        if profile.category == "military":
            data["extra"] = MilitaryProfileSerializer(user.militaryprofile).data

        elif profile.category == "paramilitary":
            data["extra"] = ParamilitarySerializer(user.paramilitaryprofile).data

        elif profile.category == "civil_servant":
            data["extra"] = CivilServantSerializer(user.civilservantprofile).data

        elif profile.category == "businessman":
            data["extra"] = BusinessSerializer(user.businessprofile).data

        return Response(data)
