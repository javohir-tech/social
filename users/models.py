import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from shared.models import BaseModel
from datetime import timedelta
from django.utils import timezone
from random import randint
from django.contrib.auth.hashers import identify_hasher
from rest_framework_simplejwt.tokens import RefreshToken


# choices
class UserRoles(models.TextChoices):
    ORDENARY_USER = "ordinary_user", "Ordinary user"
    ADMIN = "admin", "Admin"
    MANAGER = "manager", "Manager"


class AuthType(models.TextChoices):
    VIA_EMAIL = "via_email", "Via Email"
    VIA_PHONE = "via_phone", "Via Phone"


class AuthStatus(models.TextChoices):
    NEW = "new", "New"
    CODE_VERIFED = "code_verified", "Code verified"
    DONE = "done", "Done"
    PHOTO = "photo", "Photo"


# Hesh  qilinganligini tekshirish


def is_hashed(password):
    try:
        identify_hasher(password)
        return True
    except Exception:
        return False


class User(AbstractUser, BaseModel):
    user_role = models.CharField(
        max_length=31, choices=UserRoles.choices, default=UserRoles.ORDENARY_USER
    )
    auth_type = models.CharField(max_length=31, choices=AuthType.choices)
    auth_status = models.CharField(
        max_length=31, choices=AuthStatus.choices, default=AuthStatus.NEW
    )
    email = models.EmailField(null=True, blank=True, unique=True)
    phone_number = models.CharField(max_length=13, null=True, blank=True, unique=True)
    photo = models.ImageField(null=True, blank=True, upload_to="users_photo")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def create_verify_code(self, auth_type):
        code = "".join([str(randint(0, 9)) for _ in range(4)])
        UserConfirmation.objects.create(code=code, user=self, auth_type=auth_type)
        return code

    def __str__(self):
        return self.username

    def check_username(self):
        if not self.username:
            temp_username = f"instagram-{uuid.uuid4().__str__().split("-")[-1]}"

            while User.objects.filter(username=temp_username).exists():
                temp_username = f"{temp_username}{randint(1, 9)}"
            self.username = temp_username

    def check_email(self):
        if self.email:
            normalize_email = self.email.lower().strip()
            self.email = normalize_email

    def check_password(self):
        if not self.password:
            temp_password = f"password-{uuid.uuid4().__str__().split("-")[-1]}"
            self.password = temp_password

    def hashing_password(self):
        if not is_hashed(self.password):
            self.set_password(self.password)

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {"access_token": str(refresh.access_token), "refresh": str(refresh)}

    def clean(self):
        self.check_username()
        self.check_email()
        self.check_password()
        self.hashing_password()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.clean()
        else:
            self.check_email()

            if self.password and not is_hashed(self.password):
                self.set_password(self.password)

        super(User, self).save(*args, **kwargs)


EXPIRE_EMAIL = 5
EXPIRE_PHONE = 2


class UserConfirmation(BaseModel):
    code = models.CharField(max_length=4)
    auth_type = models.CharField(max_length=31, choices=AuthType.choices)
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="verify_type"
    )
    expiration_date = models.DateTimeField(null=True, blank=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.__str__()

    def save(self, *args, **kwargs):
        if self._state.adding:
            if self.auth_type == AuthType.VIA_EMAIL:
                self.expiration_date = timezone.now() + timedelta(minutes=EXPIRE_EMAIL)
            elif self.auth_type == AuthType.VIA_PHONE:
                self.expiration_date = timezone.now() + timedelta(minutes=EXPIRE_PHONE)
        super(UserConfirmation, self).save(*args, **kwargs)

    def is_expired(self):
        if self.expiration_date is None:
            return True
        return timezone.now() > self.expiration_date

    def can_verify(self):
        if self.is_confirmed:
            return False
        if self.is_expired():
            return False
        return True
