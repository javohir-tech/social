from .tokens import RegistrationToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class RegistrationTokenAuthentication(JWTAuthentication)  :
    
    def get_validated_token(self, raw_token):
        try :
            return RegistrationToken(raw_token)
        except Exception as e :
            raise AuthenticationFailed(f'Token yaroqsiz : {str(e)} ')
        
    def get_user(self, validated_token):
        try :
            from users.models import User
            user_id  = validated_token.get('user_id')

            if user_id is None : 
                raise AuthenticationFailed("Token ichida user_id yo'q")

            user = User.objects.get(id = user_id)

            if user.auth_status != validated_token.get('current_step') :
                raise AuthenticationFailed('Token eskirgan')

            return user
        except  User.DoesNotExist :
            raise AuthenticationFailed("user topilmadi")
        except Exception as e :
            raise AuthenticationFailed(f'Authenticated xatosi {str(e)}')
        