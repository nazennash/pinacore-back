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


from django.contrib.auth.backends import ModelBackend
from .models import CustomUser

class SellerBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(username=username) if username else CustomUser.objects.get(email=kwargs.get('email'))
            if user.check_password(password) and user.is_seller:
                return user
        except CustomUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None


from django.contrib.auth.backends import ModelBackend
from .models import CustomUser

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(email=username)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
