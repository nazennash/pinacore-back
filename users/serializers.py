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
        fields = ['phone_number', 'name']

    def create(self, validated_data):
        validated_data['is_buyer'] = True  # Automatically set this user as a buyer
        return super().create(validated_data)


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
        fields = ['phone_number', 'otp']



from rest_framework import serializers
from .models import CustomUser

class RegisterSellerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ['phone_number', 'username', 'email', 'name', 'password']

    def create(self, validated_data):
        validated_data['is_seller'] = True  # Mark as seller
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already in use.")
        return value


from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser

class SellerLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username and not email:
            raise serializers.ValidationError("Must include either username or email and password.")

        user = authenticate(username=username or email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid login credentials.")

        if not user.is_seller:
            raise serializers.ValidationError("User is not a seller.")

        data['user'] = user
        return data
