from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from datetime import timedelta
from django.utils import timezone

class User(AbstractUser):
    """To'liq ro'yxatdan o'tgan foydalanuvchi"""
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_registration_complete = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username or self.email or self.phone


class TempRegistration(models.Model):
    """Vaqtinchalik ro'yxatdan o'tish jarayonidagi foydalanuvchi"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Boshlang'ich ma'lumotlar
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    
    # Verification
    verification_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    
    # Username/Password (keyinchalik to'ldiriladi)
    username = models.CharField(max_length=150, null=True, blank=True)
    password_hash = models.CharField(max_length=255, null=True, blank=True)
    
    # Registratsiya bosqichi
    STEP_CHOICES = [
        ('email_sent', 'Email/Phone yuborildi'),
        ('code_verified', 'Kod tasdiqlandi'),
        ('credentials_set', 'Username/Password ornatildi'),
        ('completed', 'Tugallandi'),
    ]
    current_step = models.CharField(max_length=20, choices=STEP_CHOICES, default='email_sent')
    
    # Vaqt cheklovi
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'temp_registrations'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['expires_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # 30 daqiqa muddatli
            self.expires_at = timezone.now() + timedelta(minutes=30)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"{self.email or self.phone} - {self.current_step}"