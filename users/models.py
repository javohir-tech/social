from django.db import models
from django.contrib.auth.models import AbstractUser
from shared.models import BaseModel

ORDENARY_USER , ADMIN , MANAGER = ('ordenary_user' , 'admin' , 'manager')
VIA_EMAIL, VIA_PHONE = ('via_email' , 'via_phone')
NEW , CODE_VERIFED , DONE , PHOTO = ('new' , 'code_verifed' , 'done' , 'photo')

class User(AbstractUser , BaseModel):
    
    USER_ROLES = (
        (ORDENARY_USER , ORDENARY_USER),
        (ADMIN ,  ADMIN),
        (MANAGER , MANAGER)
    )
    
    AUTH_TYPE = (
        (VIA_EMAIL , VIA_EMAIL),
        (VIA_PHONE , VIA_PHONE)
    )
    
    AUTH_STATUS = (
        (NEW , NEW),
        (CODE_VERIFED , CODE_VERIFED),
        (DONE  , DONE),
        (PHOTO , PHOTO)
    )
    
    user_role = models.CharField(max_length=31 , choices=USER_ROLES , default=ORDENARY_USER)
    auth_type = models.CharField(max_length=31 , choices=AUTH_TYPE)
    auth_status =  models.CharField(max_length=31 , choices=AUTH_STATUS , default=NEW)
    email = models.EmailField(null=True , blank=True , unique=True)
    phone_number = models.CharField(max_length=13 , null=True,  blank=True , unique=True)
    photo = models.ImageField(null=True , blank=True, upload_to='users_photo')

