from django.shortcuts import render
from .serializers import SingUpSerializer, UpdateUserSerilazer
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from .models import User, UserConfirmation
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from rest_framework.authentication import authenticate
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from .models import AuthStatus, AuthType
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from shared.utility import send_email
from rest_framework.generics import UpdateAPIView


class SingUpView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = SingUpSerializer


class VerifyView(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        code = self.request.data.get("code")

        if self.check_code(user, code):
            tokens = user.token()
            return Response(
                data={
                    "success": True,
                    "auth_status": AuthStatus.CODE_VERIFED,
                    "access": tokens.get("access_token"),
                    "refresh_token": tokens.get("refresh"),
                }
            )

    @staticmethod
    def check_code(user, code):
        verify = user.verify.filter(
            expiration_date__gte=timezone.now(), code=code, is_confirmed=False
        )

        if not verify.exists():
            data = {
                "success": False,
                "message": "siz kiritgan kod xato yoki mudati eskirgan bolishi mumkin",
            }
            raise ValidationError(data)
        verify.update(is_confirmed=True)
        if user.auth_status == AuthStatus.NEW:
            user.auth_status = AuthStatus.CODE_VERIFED
            user.save()

        return True


class GetVerifyCode(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):

        user = self.request.user

        self.check_verifate(user)

        if user.auth_type == AuthType.VIA_EMAIL:
            code = user.create_verify_code(AuthType.VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth.type == AuthType.VIA_PHONE:
            code = user.create_verify_code(AuthType.VIA_EMAIL)
            send_email(user.email, code)
        else:
            raise ValidationError(
                {
                    "success": False,
                    "message": "email yoki tel raqam notgri  kiritilgan",
                    "error ": "erro  in GetVErifyCode  view wiews",
                }
            )

        return Response(
            {"success": True, "message": "Tastiqlash kodingiz qayta yuborildi!!!"}
        )

    @staticmethod
    def check_verifate(user):
        verifted = user.verify.filter(
            expiration_date__gte=timezone.now(), is_confirmed=False
        )
        if verifted.exists():
            data = {
                "success": False,
                "message": "Siz ga yuborilgan kod hozirda yaroqli . Biroz kuting ",
            }

            raise ValidationError(data)


class EditUserView(UpdateAPIView):
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = UpdateUserSerilazer
    http_method_names = ["put", "patch"]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        super().update(request , *args ,  **kwargs) 
        data = {
            'success' : True ,  
            'message' :'muvafiqiyatli royhatdan  otingiz ', 
            'auth_status' : self.request.user.auth_status
        }
        
        return Response(data , status=200)
        
    def partial_update(self, request, *args, **kwargs):
        super(request ,  *args , **kwargs)
        data = {
            'success' : True , 
            'message' : 'muvafiqiyatli tuzatildi'
        }
        
        return Response(data , status=200)


# Create your views here.
