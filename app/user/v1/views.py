from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.throttling import UserRateThrottle

from .constants import *
from helpers.cache_adapter import CacheAdapter
from helpers.misc_helper import get_random_number
from .serializers import RegisterUserSerializer, EmailLoginSerializer, OTPLoginSerializer, OTPGenerateSerializer


class RegisterUserView(APIView):
    """
    Creates a user in the DB
    """

    def post(self, request):
        """
        POST API -> /api/v1/user/register
        Validates and creates a User in core_user table
        """
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response({'response': 'User Created!'},
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUserView(APIView):
    """
    Authenticates a user
    """
    throttle_classes = [UserRateThrottle]

    def get_user(self, data):
        """
        Returns a User given email/mobile_number
        """
        if "email" in data:
            return get_user_model().objects.get(email=data['email'])
        else:
            return get_user_model().objects.get(
                mobile_number=data['mobile_number'])

    def get_token(self, serializer):
        """
        Returns access and refersh token for a user
        """
        if serializer.is_valid():
            user = self.get_user(serializer.data)
            refresh = TokenObtainPairSerializer.get_token(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """
        POST API -> /api/v1/user/login
        Authenticates and provides tokens to the user
        """
        data = request.data
        if "email" in data:
            serializer = EmailLoginSerializer(data=data)
        elif "mobile_number" in data:
            serializer = OTPLoginSerializer(data=data)
        else:
            return Response({'detail': 'invalid params'},
                            status=status.HTTP_400_BAD_REQUEST)

        return self.get_token(serializer)


class GenerateOTPView(APIView):
    """
    Generates OTP for user
    """

    def post(self, request):
        """
        POST API -> /api/v1/user/generate/otp
        """

        serializer = OTPGenerateSerializer(data=request.data)
        if serializer.is_valid():
            key = OTP_PREFIX + serializer.data['mobile_number']
            cache_adapter_obj = CacheAdapter()
            cache_adapter_obj.set(
                key, get_random_number(), OTP_EXPIRY_IN_SECONDS)

            return Response({'response': 'OTP sent'},
                            status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
