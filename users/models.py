from django.db import models
from django.contrib.auth.models import AbstractUser
from shared.models import BaseModel

# choices 
class UserRoles(models.TextChoices):
    ORDENARY_USER = "ordinary_user", "Ordinary user"
    ADMIN = "admin", "Admin"
    MANAGER = "manager", "Manager"
    
class AuthType(models.TextChoices) :
    VIA_EMAIL = 'via_email' , 'Via Email'
    VIA_PHONE = 'via_phone' , 'Via Phone'
    
class AuthStatus(models.TextChoices) :
    NEW = 'new' , 'New'
    CODE_VERIFED = 'code_verified' , 'Code verified'
    DONE = 'done' , 'Done'
    PHOTO = 'photo' , 'Photo'


class User(AbstractUser, BaseModel):

    user_role = models.CharField(
        max_length=31, choices=UserRoles.choices, default=UserRoles.ORDENARY_USER
    )
    auth_type = models.CharField(max_length=31, choices=AuthType.choices)
    auth_status = models.CharField(max_length=31, choices=AuthStatus.choices, default=AuthStatus.NEW)
    email = models.EmailField(null=True, blank=True, unique=True)
    phone_number = models.CharField(max_length=13, null=True, blank=True, unique=True)
    photo = models.ImageField(null=True, blank=True, upload_to="users_photo")
