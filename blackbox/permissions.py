from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken
from .models import TempRegistration
from django.utils import timezone

class IsRegistrationToken(BasePermission):
    """
    Faqat registration token bilan kirish mumkin.
    Oddiy access token bilan KIRISH MUMKIN EMAS!
    """
    
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return False
        
        token_str = auth_header.split(' ')[1]
        
        try:
            # Token-ni decode qilish
            token = UntypedToken(token_str)
            
            # 1. Token turi tekshirish
            if token.get('token_type') != 'registration':
                return False
            
            # 2. TempRegistration mavjudligini tekshirish
            temp_user_id = token.get('user_id')
            temp_user = TempRegistration.objects.filter(id=temp_user_id).first()
            
            if not temp_user:
                return False
            
            # 3. Vaqt tugaganligini tekshirish
            if temp_user.is_expired():
                return False
            
            # Request obyektiga temp_user qo'shish
            request.temp_user = temp_user
            request.registration_token = token
            
            return True
            
        except (InvalidToken, TokenError):
            return False


class IsRegistrationStepAllowed(BasePermission):
    """
    Foydalanuvchi hozirgi bosqichida bu action ni bajara oladimi?
    """
    
    # View-da required_step o'rnatilishi kerak
    def has_permission(self, request, view):
        if not hasattr(request, 'temp_user'):
            return False
        
        required_steps = getattr(view, 'required_steps', [])
        
        if not required_steps:
            return True
        
        return request.temp_user.current_step in required_steps


class IsFullyAuthenticated(BasePermission):
    """
    Faqat to'liq ro'yxatdan o'tgan foydalanuvchilar uchun.
    Registration token bilan KIRISH MUMKIN EMAS!
    """
    
    def has_permission(self, request, view):
        # 1. User autentifikatsiya qilinganmi?
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 2. Token registration token emasligini tekshirish
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token_str = auth_header.split(' ')[1]
            try:
                token = UntypedToken(token_str)
                if token.get('token_type') == 'registration':
                    # Registration token bilan kirish taqiqlangan!
                    return False
            except (InvalidToken, TokenError):
                return False
        
        # 3. Registratsiya tugallanganmi?
        if not request.user.is_registration_complete:
            return False
        
        return True