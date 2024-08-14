from django.contrib.auth.backends import BaseBackend
from .models import CustomUser

class CombinedBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, phone_number=None, otp=None, **kwargs):
        if phone_number and otp:
            return self.authenticate_with_otp(phone_number, otp)
        elif username:
            return self.authenticate_with_username_or_email(username, password)
        return None

    def authenticate_with_otp(self, phone_number, otp):
        try:
            user = CustomUser.objects.get(phone_number=phone_number, otp=otp)
            print(user)
            user.otp = None
            print(user)
            user.save()
            return user
        except CustomUser.DoesNotExist:
            return None

    def authenticate_with_username_or_email(self, username, password):
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(email=username)
            except CustomUser.DoesNotExist:
                return None

        if user.check_password(password):
            if hasattr(user, 'is_seller') and not user.is_seller:
                return None
            return user
        return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
