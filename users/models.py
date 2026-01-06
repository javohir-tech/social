from django.db import models
from django.contrib.auth.models import AbstractUser
from shared.models import BaseModel
from datetime import timedelta
from django.utils import timezone
from random import randint


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
        code  = ''.join([str(randint(0, 9)) for _ in range(4)])
        UserConfirmation.objects.create(
            code = code,
            user = self,
            auth_type = auth_type
        )

EXPIRE_EMAIL = 5
EXPIRE_PHONE = 2


class UserConfirmation(BaseModel):
    code = models.CharField(max_length=4)
    auth_type = models.CharField(max_length=31, choices=AuthType.choices)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="verify_type")
    expiration_date = models.DateTimeField(null=True, blank=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.__str__()

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.auth_type == AuthType.VIA_EMAIL:
                self.expiration_date = timezone.now() + timedelta(minutes=EXPIRE_EMAIL)
            elif self.auth_type == AuthType.VIA_PHONE:
                self.expiration_date = timezone.now() + timedelta(minutes=EXPIRE_PHONE)
        super(UserConfirmation, self).save(*args, **kwargs)
