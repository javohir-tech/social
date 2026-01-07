from .models import User, UserConfirmation, AuthStatus, AuthType
from rest_framework import serializers, exceptions
from shared.utility import check_email_or_phone


class SingUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # barcha filedlar tayyorlanip olinadi shundan song dinamik fiel qoshsa boladi 
        self.fields["email_or_phone"] = serializers.CharField(max_length=31)

    class Meta:
        model = User
        fields = ("id", "auth_type", "auth_status")
        extra_kwargs = {
            "auth_type": {"read_only": True, "required": False},
            "auth_status": {"read_only": True, "required": False},
        }

    def validate(self, data):
        super().validate(data) # bu fieldslarga qoshilgan barcha validatsiyalaarni tekshirip oladi 
        data = self.auth_validate(data)
        return data

    @staticmethod
    def auth_validate(data):
        print(data)
        user_input = str(data["email_or_phone"]).lower()
        auth_type = check_email_or_phone(user_input)
        print("user_input", user_input)
        print("auth_type", auth_type)
        return data
