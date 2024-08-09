from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number=None, username=None, email=None, password=None, **extra_fields):
        if not email and not username:
            raise ValueError('The given email or username must be set')
        
        if email:
            email = self.normalize_email(email)
        user = self.model(phone_number=phone_number, username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number=None, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_buyer', True)
        extra_fields.setdefault('is_seller', True)

        return self.create_user(phone_number, username, email, password, **extra_fields)
    
class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = PhoneNumberField(blank=True, null=True, unique=True, default=None)
    otp = models.CharField(max_length=4, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True, default="User")

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_buyer = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'  # For admin login
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']  # Required for sellers

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.email if self.email else self.username or self.phone_number}'

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.__class__.objects.normalize_email(self.email)
        super().save(*args, **kwargs)
