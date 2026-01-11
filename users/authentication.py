"""
users/authentication.py
Registratsiya tokeni uchun maxsus authentication class
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from users.tokens import RegistrationToken


class RegistrationTokenAuthentication(JWTAuthentication):
    """
    
    Faqat registratsiya tokenlarini qabul qiladi
    
    """
    
    def get_validated_token(self, raw_token):
        """
        Token validatsiya qilish
        """
        try:
            return RegistrationToken(raw_token)
        except Exception as e:
            raise AuthenticationFailed(f'Token yaroqsiz: {str(e)}')
    
    def get_user(self, validated_token):
        """
        Token'dan userni olish
        """
        try:
            from users.models import User
            user_id = validated_token.get('user_id')
            
            if user_id is None:
                raise AuthenticationFailed('Token ichida user_id yo\'q')
            
            user = User.objects.get(id=user_id)
            
            # User'ning auth_status'i token'dagi step bilan mos kelishi kerak
            if user.auth_status != validated_token.get('current_step'):
                raise AuthenticationFailed('Token eskirgan. Yangi token oling.')
            
            return user
            
        except User.DoesNotExist:
            raise AuthenticationFailed('User topilmadi')
        except Exception as e:
            raise AuthenticationFailed(f'Authentication xatosi: {str(e)}')