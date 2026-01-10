from .models import User, UserConfirmation, AuthStatus, AuthType
from rest_framework import serializers, exceptions
from shared.utility import check_email_or_phone, send_email, check_auth_type
from rest_framework.exceptions import ValidationError, PermissionDenied , NotFound
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.generics import get_object_or_404
from django.contrib.auth.models import update_last_login
from django.db.models import Q


class SingUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(SingUpSerializer, self).__init__(
            *args, **kwargs
        )  # barcha fieldlar tayyorlanip olinadi shundan song dinamik fiel qoshsa boladi
        self.fields["email_or_phone"] = serializers.CharField(
            max_length=31, write_only=True
        )

    class Meta:
        model = User
        fields = ("id", "auth_type", "auth_status")
        extra_kwargs = {
            "auth_type": {"read_only": True, "required": False},
            "auth_status": {"read_only": True, "required": False},
        }

    def create(self, validated_data):
        user = User(**validated_data)
        # user.clean()
        user.save()
        if validated_data["auth_type"] == AuthType.VIA_EMAIL:
            code = user.create_verify_code(AuthType.VIA_EMAIL)
            # print("=" * 50 )
            send_email(user.email, code)
            pass
        elif validated_data["auth_type"] == AuthType.VIA_PHONE:
            code = user.create_verify_code(AuthType.VIA_PHONE)
            print(code)
            pass

        return user

    def validate(self, data):
        super(SingUpSerializer, self).validate(data)
        # bu fieldslarga qoshilgan barcha validatsiyalaarni tekshirip oladi
        data = self.auth_validate(data)
        data = self.check_user_exists(data)

        return data

    @staticmethod
    def auth_validate(data):
        user_input = str(data["email_or_phone"]).lower()
        auth_type = check_email_or_phone(user_input)
        if auth_type == AuthType.VIA_EMAIL:
            data = {"email": user_input, "auth_type": AuthType.VIA_EMAIL}
        elif auth_type == AuthType.VIA_PHONE:
            data = {"phone_number": user_input, "auth_type": AuthType.VIA_PHONE}
        else:
            data = {"success": False, "message": "email yoki telefon raqam hato"}
            raise exceptions.ValidationError(data)

        # print("data", data)

        return data

    @staticmethod
    def check_user_exists(data):
        auth_type = data.get("auth_type")
        if auth_type == AuthType.VIA_EMAIL:
            email_input = data.get("email")
            if User.objects.filter(email=email_input).exists():
                raise ValidationError(
                    {"success": False, "message": "ushbu emaildan oldin foydalanilgan"}
                )
        elif auth_type == AuthType.VIA_PHONE:
            phone = data.get("phone_number")
            if User.objects.filter(phone_number=phone).exists():
                raise ValidationError(
                    {"success": False, "message": "ushbu raqamdan oldin foydalanilgan"}
                )
        return data

    def to_representation(self, instance):
        data = super(SingUpSerializer, self).to_representation(instance)
        data.update(instance.token())

        return data


class UpdateUserSerilazer(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        password = data.get("password", None)
        confirm_password = data.get("confirm_password", None)

        if not password == confirm_password:
            data = {
                "success": True,
                "message": "sizning parolingiz va tastiqlash parolingiz mos emas . qayta urunip ko'ring",
            }

            raise ValidationError(data)
        if password:
            validate_password(password)
            validate_password(confirm_password)

        return data

    def validate_username(self, username):
        if len(username) < 8 or len(username) > 30:
            data = {
                "success": False,
                "message": "username must be between 8 and 30 characters long",
            }

            raise ValidationError(data)
        if username.isdigit():
            data = {
                "success": False,
                "message": "username harflardan iborat bolishi kerak va belgilardan iborat bolishi kerak ",
            }

            raise ValidationError(data)

        return username

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.password = validated_data.get("password", instance.password)
        instance.username = validated_data.get("username", instance.username)

        if validated_data.get("password"):
            instance.set_password(validated_data.get("password"))
        if instance.auth_status == AuthStatus.CODE_VERIFED:
            instance.auth_status = AuthStatus.DONE
        instance.save()

        return instance


class ChangeUserPhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField(
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "heic", "heif"]
            )
        ]
    )

    def update(self, instance, validated_data):
        photo_input = validated_data.get("photo_input", instance.photo)

        if photo_input:
            instance.photo = photo_input
            instance.auth_status = AuthStatus.PHOTO_Done
            instance.save()

        return instance


class SingInSerializer(TokenObtainPairSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"] = serializers.CharField(read_only=True, required=False)
        self.fields["user_input"] = serializers.CharField(required=True)

    def validate(self, data):
        data = self.auth_validate(data)
        user = data.get("user")
        data = user.token()
        data["auth_status"] = user.auth_status
        data["full_name"] = user.full_name

        return data

    def auth_validate(self, data):
        user_input = data.get("user_input")
        login_type = check_auth_type(user_input)

        if login_type == "username":
            username = user_input
        elif login_type == AuthType.VIA_EMAIL:
            username = self.get_user(email__iexact=user_input)
        elif login_type == AuthType.VIA_PHONE:
            username = self.get_user(phone_number=user_input)

        current_user = User.objects.get(username=username)

        if current_user and current_user.auth_status in [
            AuthStatus.NEW,
            AuthStatus.CODE_VERIFED,
        ]:
            raise PermissionDenied("Siz to'liq ro'yhatdan o'tmagansiz")

        user = authenticate(username=current_user.username, password=data["password"])

        if user is not None:
            data["user"] = user
        else:
            raise ValidationError(
                {
                    "success": False,
                    "message": "Sorry, login or password you entered is incorrect. Please check and trg again!",
                }
            )

        return data

    @staticmethod
    def get_user(**kwargs):
        user = User.objects.filter(**kwargs)
        if not user.exists():
            raise ValidationError(
                {"success": False, "message": "No active account found"}
            )

        return user.first()


# ////////////////////////////////
# ///// REFRESH SERIALIZER ///////
# ////////////////////////////////
class LoginRefreshSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        access_token_instance = AccessToken(data["access"])
        user_id = access_token_instance["user_id"]
        user = get_object_or_404(User, id=user_id)
        update_last_login(None, user)
        data["refresh"] = attrs["refresh"]

        return data


# ///////////////////////////////////////
# ///////////// LOG OUT /////////////////
# ///////////////////////////////////////


class LogOutSerializer(serializers.Serializer):

    refresh = serializers.CharField()


# //////////////////////////////////////////
# ////////// FORGET PASSWORD ///////////////
# //////////////////////////////////////////
class ForgetPasswordSerializer(serializers.Serializer):

    user_input = serializers.CharField()

    def validate(self, data):
        user_input = data.get("user_input", None)
        if user_input is None:
            raise ValidationError(
                {"success": False, "message": "maydon toldirilishi shart"}
            )
        check_auth_type(user_input)
        user = User.objects.filter(
            Q(username=user_input) | Q(email=user_input) | Q(phone_number=user_input)
        )
        
        if not user.exists() :
            raise  ValidationError({
                "success" : False,  
                "message" :"user not found"
            })
        data['user'] = user.first()
        
        return data