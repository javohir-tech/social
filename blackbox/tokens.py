from rest_framework_simplejwt.tokens import Token
from datetime import timedelta

class RegistrationToken(Token):
    """
    Faqat ro'yxatdan o'tish jarayoni uchun maxsus token.
    Bu token bilan asosiy tizim funksiyalariga kirish mumkin emas!
    """
    token_type = 'registration'
    lifetime = timedelta(minutes=15)
    
    @classmethod
    def for_temp_user(cls, temp_registration):
        """
        TempRegistration obyekti uchun token yaratish
        """
        token = cls()
        
        # Token payload-iga maxsus ma'lumotlar
        token['user_id'] = str(temp_registration.id)
        token['token_type'] = 'registration'
        token['current_step'] = temp_registration.current_step
        token['is_verified'] = temp_registration.is_verified
        
        # Email yoki phone
        if temp_registration.email:
            token['email'] = temp_registration.email
        if temp_registration.phone:
            token['phone'] = temp_registration.phone
        
        return token


class RegistrationStepPermission:
    """
    Har bir registration step uchun ruxsat tekshirish
    """
    
    STEP_REQUIREMENTS = {
        'verify_code': ['email_sent'],
        'set_credentials': ['code_verified'],
        'upload_photo': ['credentials_set'],
    }
    
    @staticmethod
    def check_permission(current_step, required_action):
        """
        Foydalanuvchi hozirgi bosqichida kerakli action ni bajara oladimi?
        """
        allowed_steps = RegistrationStepPermission.STEP_REQUIREMENTS.get(required_action, [])
        return current_step in allowed_steps