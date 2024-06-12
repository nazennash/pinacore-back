from django.contrib.auth.backends import BaseBackend
from .models import CustomUser

class OTPBackend(BaseBackend):
    def authenticate(self, request, phone_number=None, otp=None):
        try:
            user = CustomUser.objects.get(phone_number=phone_number, otp=otp)
            return user
        except CustomUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
