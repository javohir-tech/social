from django.shortcuts import render
from .serializers import SingUpSerializer
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from .models import User, UserConfirmation
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from rest_framework.authentication import authenticate
from django.utils import timezone
from rest_framework.exceptions import  ValidationError
from .models import AuthStatus
from rest_framework.response import Response
from rest_framework.decorators  import permission_classes

class SingUpView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = SingUpSerializer


class VerifyView(APIView):

    permission_classes = (IsAuthenticated , )

    def post(self, request, *args, **kwargs):
        user = self.request.user
        code = self.request.data.get("code")
        

        if self.check_code(user, code) :
            tokens = user.token()
            return Response(
                data = {
                    'success' : True , 
                    'auth_status' : AuthStatus.CODE_VERIFED ,  
                    'access' : tokens.get('access_token'),
                    'token' : tokens.get("refresh")
                }
            )

    @staticmethod
    def check_code(user, code):
        verify = user.verify.filter(
            expiration_date__gte=timezone.now(),
            code=code,
            is_confirmed = False
        )
        
        if not verify.exists() :
            data = {
                'success' : False,
                'message' : 'siz kiritgan kod xato yoki mudati eskirgan bolishi mumkin'
            }
            raise ValidationError(data)
        verify.update(is_confirmed = True)
        if user.auth_status == AuthStatus.NEW :
           user.auth_status = AuthStatus.CODE_VERIFED
           user.save()
            
        return True
            


# Create your views here.
