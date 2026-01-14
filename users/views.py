from django.shortcuts import render
from .serializers import (
    SingUpSerializer,
    UpdateUserSerilazer,
    ChangeUserPhotoSerializer,
    SingInSerializer,
    LoginRefreshSerializer,
    LogOutSerializer,
    ForgetPasswordSerializer,
    PasswordResetSerializer,
)
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from .models import User, UserConfirmation
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import permissions
from rest_framework.authentication import authenticate
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from .models import AuthStatus, AuthType
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from shared.utility import send_email
from rest_framework.generics import UpdateAPIView
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.hashers import check_password
from .permissions import IsRegistartionToken, CanAccessStep2 , CanAccessStep3
from .tokens import RegistrationToken
from .authentication import RegistrationTokenAuthentication


class SingUpView(CreateAPIView):

    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = SingUpSerializer


class VerifyView(APIView):

    authentication_classes = [RegistrationTokenAuthentication]
    permission_classes = ( IsRegistartionToken, CanAccessStep2 , )

    def post(self, request, *args, **kwargs):
        user = self.request.user
        code = self.request.data.get("code")

        if self.check_code(user, code):
            # tokens = user.token()
            token = RegistrationToken.for_user(user)
            return Response(
                data={
                    "success": True,
                    "auth_status": AuthStatus.CODE_VERIFED,
                    # "access": tokens.get("access_token"),
                    # "refresh_token": tokens.get("refresh"),
                    "token" : str(token)
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
            {
                "success": True,
                "message": "Tastiqlash kodingiz qayta yuborildi!!!",
                "access_token": user.token().get("access_token"),
            }
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


class EditUserView(APIView):

    authentication_classes = [RegistrationTokenAuthentication]
    permission_classes = [IsRegistartionToken , CanAccessStep3]

    def put(self, request, *args, **kwargs):

        serializer = UpdateUserSerilazer(
            instance=self.request.user, data=self.request.data
        )

        if serializer.is_valid():
            serializer.save()
            tokens = self.request.user.token()
            token = RegistrationToken.for_user(self.request.user)
            return Response(
                {
                    "success": True,
                    "message": "Yangilandi",
                    "auth_status": self.request.user.auth_status,
                    "token" : str(token),
                    "success_token"  : tokens.get("access_token"),
                    "refresh" : tokens.get("refresh")
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):

        serializer = UpdateUserSerilazer(
            instance=self.request.user, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Tuzatildi",
                    "auth_status": self.request.user.auth_status,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeUserPhotoView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):

        serializer = ChangeUserPhotoSerializer(instance=request.user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Rasm muvvafiqiyatli yuklandi"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    serializer_class = SingInSerializer


# ///////////////////////////////////////////
# /////// REFRESH TOKEN CREATE //////////////
# ///////////////////////////////////////////
class RefreshTokenView(TokenRefreshView):
    serializer_class = LoginRefreshSerializer


# /////////////////////////////////////////////////////////////////////////
# ///////////////////// LOGOUT        /////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////
class LogOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        serializer = LogOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh = request.data["refresh"]
            token = RefreshToken(refresh)
            token.blacklist()
            return Response({"success": True, "message": "you are success logout"})
        except TokenError:
            return Response(status=400)


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////// PASSWORD FORGOT ///////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class ForgetPasswordView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ForgetPasswordSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        if user.auth_type == AuthType.VIA_EMAIL:
            code = user.create_verify_code(AuthType.VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type == AuthType.VIA_PHONE:
            code = user.create_verify_code(AuthType.VIA_PHONE)
            send_email(user.email, code)

        token = user.token()
        return Response(
            {
                "success": "True",
                "message": "usr topildi",
                "access_token": token.get("access_token"),
                "refresh_token": token.get("refresh"),
                "user_status": user.auth_status,
            },
            status=status.HTTP_200_OK,
        )


# ////////////////////////////////////////////////////////////////////////////////////////////
# /////////////////////////// PASSWORD RESET /////////////////////////////////////////////////
# ////////////////////////////////////////////////////////////////////////////////////////////


class RestPasswordVerifyView(APIView):

    def post(self, request, *args, **kwargs):

        user_confirm = self.request.user.verify.filter(
            expiration_date__gte=timezone.now()
        ).first()
        code = user_confirm.code

        if code != request.data["code"]:
            raise ValidationError(
                {"success": False, "message": "Siz kiritgan kod to'g'ri emas"}
            )

        token = self.request.user.token()

        return Response(
            {
                "success": False,
                "message": "parolni o'zgartirishingiz mumkin",
                "access_token": token.get("access_token"),
                "refresh": token.get("refresh"),
                "auth_satus": self.request.user.auth_status,
            }
        )


class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordResetSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            instance=self.request.user, data=self.request.data, partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "success": True,
                "message": "parol muvvafaqiyatli o'zgartirldi",
                "auth_status": request.user.auth_status,
            }
        )
