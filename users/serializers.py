from rest_framework import serializers
from .models import CustomUser


def validate_phone_number(value):
    if not (value.startswith('+')):
        raise serializers.ValidationError("Phone number must start with + or a country code.")
    if len(value) > 13:
        raise serializers.ValidationError("Phone number must be less than 12 characters.")
    if len(value) != 13:
        raise serializers.ValidationError("Phone number must be 13 characters.")
    return value


class RegisterUserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=[validate_phone_number])
    class Meta:
        model = CustomUser
        fields = ['phone_number','name']

class RequestOTPSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=[validate_phone_number])
    class Meta:
        model = CustomUser
        fields = ['phone_number']

class VerifyOTPSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=[validate_phone_number])
    otp = serializers.CharField()
    class Meta:
        model = CustomUser
        fields = ['phone_number','otp']
