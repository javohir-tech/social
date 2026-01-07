from django.shortcuts import render
from .serializers import SingUpSerializer
from rest_framework.generics import CreateAPIView
from .models import User, UserConfirmation
from rest_framework import permissions


class SingUpView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = SingUpSerializer


# Create your views here.
