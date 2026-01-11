from rest_framework_simplejwt.tokens import Token
from datetime import timedelta
from django.utils import timezone


class RegistrationToken(Token):

    token_type = "registration"
    lifetime = timedelta(minutes=15)

    @classmethod
    def for_user(cls, user):

        token = cls()
        token["user_id"] = str(user.id)
        token["token_type"] = "registration"
        token["current_step"] = user.auth_status
        token["auth_type"] = user.auth_type

        if user.email:
            token["email"] = user.email
        if user.phone_number:
            token["phone_number"] = user.phone_number

        if user.username and not user.username.startswith("instagram-"):
            token["username"] = user.username

        return token

    @classmethod
    def get_user_from_token(cls, token_str):
        try:
            from .models import User

            token = cls(token_str)
            user_id = token.get("user_id")
            return User.objects.get(id=user_id)
        except Exception:
            return None
