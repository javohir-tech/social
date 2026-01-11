from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken
from .models import User , AuthStatus
from django.utils import timezone

class IsRegistartionToken(BasePermission):
    
    message = "Faqat registratsiya tokeni bilan kirish mumkin"

    def has_permission(self, request, view):

        if not hasattr(request, "auth") or request.auth is None:
            return False

        token_type = request.auth.get("token_type")

        return token_type == "registration"
    
class CanAccessStep2(BasePermission) :
    
    def has_permission(self, request, view):
        
        if not hasattr(request , 'auth') or request.auth is None :
            return False
        
        current_step = request.auth.get('current_step')
        
        return current_step == AuthStatus.NEW
    
# class CanAccessStep3(BasePermission):
#     """
#     3-bosqichga kirish: Username va password kiritish
#     Faqat 'code_verified' statusdagi userlar kirishi mumkin
#     """
#     message = "Bu bosqichga kirishga ruxsatingiz yo'q. Avval kodni tasdiqlang."
    
#     def has_permission(self, request, view):
#         if not hasattr(request, 'auth') or request.auth is None:
#             return False
        
#         # Token type tekshirish
#         if request.auth.get('token_type') != 'registration':
#             return False
        
#         # Current step tekshirish
#         current_step = request.auth.get('current_step')
#         return current_step == AuthStatus.CODE_VERIFED


# class CanAccessStep4(BasePermission):
#     """
#     4-bosqichga kirish: Rasm yuklash (optional)
#     Faqat 'done' statusdagi userlar kirishi mumkin
#     """
#     message = "Bu bosqichga kirishga ruxsatingiz yo'q. Avval username va password kiriting."
    
#     def has_permission(self, request, view):
#         if not hasattr(request, 'auth') or request.auth is None:
#             return False
        
#         # Token type tekshirish
#         if request.auth.get('token_type') != 'registration':
#             return False
        
#         # Current step tekshirish
#         current_step = request.auth.get('current_step')
#         return current_step == AuthStatus.DONE


# class IsRegistrationComplete(BasePermission):
#     """
#     Registratsiya tugallanganligini tekshirish
#     'photo_done' yoki 'done' statusdagi userlar
#     """
#     message = "Registratsiyangiz hali tugallanmagan"
    
#     def has_permission(self, request, view):
#         if not hasattr(request, 'auth') or request.auth is None:
#             return False
        
#         current_step = request.auth.get('current_step')
#         return current_step in [AuthStatus.DONE, AuthStatus.PHOTO_Done]

