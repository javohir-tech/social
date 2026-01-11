from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from .models import TempRegistration, User
from .permissions import (
    IsRegistrationToken,
    IsRegistrationStepAllowed,
    IsFullyAuthenticated,
)
from .tokens import RegistrationToken
from .serializers import (
    StartRegistrationSerializer,
    VerifyCodeSerializer,
    SetCredentialsSerializer,
)
import random
import string


class StartRegistrationView(APIView):
    """
    1-QADAM: Email yoki telefon raqam yuborish
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StartRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        phone = serializer.validated_data.get("phone")

        # Verification kod generatsiya qilish
        verification_code = "".join(random.choices(string.digits, k=6))

        # TempRegistration yaratish
        temp_user = TempRegistration.objects.create(
            email=email,
            phone=phone,
            verification_code=verification_code,
            current_step="email_sent",
        )

        # SMS/Email yuborish (bu yerda sizning SMS service)
        # send_verification_code(email or phone, verification_code)

        # Registration token yaratish
        token = RegistrationToken.for_temp_user(temp_user)

        return Response(
            {
                "message": "Verification kod yuborildi",
                "registration_token": str(token),
                "temp_user_id": str(temp_user.id),
                "expires_in": 900,  # 15 daqiqa
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyCodeView(APIView):
    """
    2-QADAM: Verification kodni tasdiqlash
    """

    permission_classes = [IsRegistrationToken, IsRegistrationStepAllowed]
    required_steps = ["email_sent"]

    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]
        temp_user = request.temp_user

        # Kodni tekshirish
        if temp_user.verification_code != code:
            return Response(
                {"error": "Noto'g'ri kod"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Verification muvaffaqiyatli
        temp_user.is_verified = True
        temp_user.current_step = "code_verified"
        temp_user.save()

        # Yangi token yaratish (yangilangan step bilan)
        new_token = RegistrationToken.for_temp_user(temp_user)

        return Response(
            {
                "message": "Kod tasdiqlandi",
                "registration_token": str(new_token),
                "next_step": "set_credentials",
            }
        )


class SetCredentialsView(APIView):
    """
    3-QADAM: Username va parol o'rnatish
    """

    permission_classes = [IsRegistrationToken, IsRegistrationStepAllowed]
    required_steps = ["code_verified"]

    def post(self, request):
        serializer = SetCredentialsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        temp_user = request.temp_user
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        # Username mavjudligini tekshirish
        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Bu username band"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Haqiqiy User yaratish
        user = User.objects.create(
            username=username,
            email=temp_user.email,
            phone=temp_user.phone,
            password=make_password(password),
            is_registration_complete=False,  # Rasm yuklanmagan
        )

        # TempRegistration yangilash
        temp_user.username = username
        temp_user.current_step = "credentials_set"
        temp_user.save()

        # HAQIQIY access va refresh tokenlar yaratish
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Account yaratildi",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "phone": user.phone,
                },
                "next_step": "upload_photo (optional)",
            },
            status=status.HTTP_201_CREATED,
        )


class UploadProfilePhotoView(APIView):
    """
    4-QADAM: Profile rasmini yuklash (ixtiyoriy)
    Bu yerda endi HAQIQIY access token kerak!
    """

    permission_classes = [IsFullyAuthenticated]

    def post(self, request):
        user = request.user

        if "image" not in request.FILES:
            return Response(
                {"error": "Rasm yuklanmadi"}, status=status.HTTP_400_BAD_REQUEST
            )

        user.profile_image = request.FILES["image"]
        user.is_registration_complete = True
        user.save()

        return Response(
            {
                "message": "Profile rasm yuklandi",
                "profile_image_url": user.profile_image.url,
            }
        )


class SkipProfilePhotoView(APIView):
    """
    Profile rasmni o'tkazib yuborish
    """

    permission_classes = [IsFullyAuthenticated]

    def post(self, request):
        user = request.user
        user.is_registration_complete = True
        user.save()

        return Response({"message": "Registratsiya tugallandi"})
