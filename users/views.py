from django.shortcuts import render
from .serializers import RegisterUserSerializer,RequestOTPSerializer, VerifyOTPSerializer
from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
import random
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        # print(serializer)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            if CustomUser.objects.filter(phone_number=phone_number).exists():
                return Response({"message":"user exists"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({"message":"user created"},status=status.HTTP_200_OK)
        else:
            return Response({"message":"invalid otp"},status=status.HTTP_400_BAD_REQUEST)

class RequestOTPView(APIView):
    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        # print(serializer)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            # print(phone_number)
            try:
                user = CustomUser.objects.get(phone_number=phone_number)
                otp = str(random.randint(1000, 9999))
                user.otp = otp
                user.save()
                return Response({"message":f"OTP sent to {phone_number}"},status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"message":"user does not exist"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"invalid input"},status=status.HTTP_400_BAD_REQUEST)
   

class VerifyOTPView(APIView):
    
    def patch(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        # print(serializer)

        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            otp = serializer.validated_data['otp']
            user = authenticate(request, phone_number=phone_number, otp=otp)
            name = CustomUser.objects.get(phone_number=phone_number).name

            # print(name)

            if user is not None:
                user.otp = None  
                user.save()
                login(request, user)
                
                # print("one",user)

                refresh = RefreshToken.for_user(user)
                token_data = {
                    'message': 'success',
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'name': str(name),
                    'phone_number': str(user),
                }
                # print('two',token_data)
                
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
