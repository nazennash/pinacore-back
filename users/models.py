from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number,  **extra_fields):
        if not phone_number:
            raise ValueError('The given phone number must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_buyer', True)
        extra_fields.setdefault('is_seller', True)

        
        user = self.create_user(phone_number, **extra_fields)
        return user
    
class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = PhoneNumberField(blank=True, null=True, unique=True, default=None)
    otp = models.CharField(max_length=4, null=True, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True, default="User")

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_buyer = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'

    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.phone_number}'
