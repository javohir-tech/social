from .models import User, UserConfirmation, AuthStatus, AuthType
from rest_framework import serializers, exceptions
from shared.utility import check_email_or_phone , send_email


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
        #user.clean()
        user.save()
        if validated_data["auth_type"] == AuthType.VIA_EMAIL:
            code = user.create_verify_code(AuthType.VIA_EMAIL)
            # print("=" * 50 )
            send_email(user.email , code)
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
