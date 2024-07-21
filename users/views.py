from django.shortcuts import render
from .serializers import RegisterUserSerializer, RequestOTPSerializer, VerifyOTPSerializer
from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
import random
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated
import requests
import json

x_username = "nazennash_42"
x_apikey = "ohid_JQzd9Gf2yKCbPSwWo8A9gtzBTMbj7GARiXgmbMmnnUJSS"
sendMessageURL = "https://api.onehub.co.ke/v1/sms/send"

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            if CustomUser.objects.filter(phone_number=phone_number).exists():
                return Response({"message": "user exists"}, status=status.HTTP_401_UNAUTHORIZED)
            serializer.save()
            return Response({"message": "user created"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "invalid otp"}, status=status.HTTP_400_BAD_REQUEST)

class RequestOTPView(APIView):
    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            try:
                user = CustomUser.objects.get(phone_number=phone_number)
                otp = str(random.randint(1000, 9999))
                user.otp = otp
                user.save()

                print(user)
                
                # Send OTP via SMS
                params = {
                    "phoneNumbers": phone_number,
                    "message": f"Your OTP is {otp}",
                    "senderId": "Onehub",
                }

                headers = {
                    'Content-type': 'application/json',
                    'Accept': 'application/json',
                    'x-api-user': x_username,
                    'x-api-key': x_apikey
                }

                print('two')
                try:
                    req = requests.post(sendMessageURL, data=json.dumps(params), headers=headers)
                    req.raise_for_status()
                    print('three')
                except requests.RequestException as e:
                    print('four')
                    return Response({"message": f"Failed to send OTP: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                return Response({"message": f"OTP sent to {phone_number}"}, status=status.HTTP_200_OK)
            
            except CustomUser.DoesNotExist:
                return Response({"message": "user does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "invalid input"}, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    def patch(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            otp = serializer.validated_data['otp']
            user = authenticate(request, phone_number=phone_number, otp=otp)
            name = CustomUser.objects.get(phone_number=phone_number).name

            if user is not None:
                user.otp = None  
                user.save()
                login(request, user)

                refresh = RefreshToken.for_user(user)
                token_data = {
                    'message': 'success',
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'name': str(name),
                    'phone_number': str(user),
                }
                return Response(token_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        if request.user.is_authenticated:
            logout(request)
            return Response({'detail': f'{request.user} logged out successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'No user was logged in.'}, status=status.HTTP_400_BAD_REQUEST)
