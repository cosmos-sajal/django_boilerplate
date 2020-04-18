from django.views import View
from django.contrib.auth import get_user_model
from django.template import RequestContext
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, render_to_response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.throttling import UserRateThrottle

from worker.tasks import send_welcome_email, send_reset_password_email
from .constants import OTP_PREFIX, OTP_EXPIRY_IN_SECONDS, EMAIL_EXPIRY_IN_SECONDS
from helpers.cache_adapter import CacheAdapter
from helpers.misc_helper import get_random_number, get_random_string, \
    get_domain_url
from .serializers import RegisterUserSerializer, EmailLoginSerializer, \
    OTPLoginSerializer, OTPGenerateSerializer, PasswordResetMailSerializer
from .forms import PasswordResetForm


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
            send_welcome_email.delay(
                request.data['email'], request.data['name'])

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


class PasswordResetView(View):
    form_class = PasswordResetForm
    template_name = 'user/reset_password_form.html'

    def get(self, request, **kwargs):
        form = self.form_class()

        return render(request, self.template_name, context={'form': form})

    def post(self, request, uid, *arg, **kwargs):
        form = self.form_class(request.POST)
        key = 'password_reset:' + uid
        cache_adapter_obj = CacheAdapter()
        email = cache_adapter_obj.get(key)
        if email is None:
            messages.error(
                request, 'The reset password link is no longer valid.')

        if form.is_valid():
            new_password = form.cleaned_data['password']
            user = get_user_model().objects.get(email=email)
            user.set_password(new_password)
            user.save()
            cache_adapter_obj.delete(key)
            messages.success(request, 'Password has been reset.')
        else:
            messages.error(
                request, 'Password reset has been unsuccessful.')

        return render(request, self.template_name, context={'form': form})


class PasswordResetMailView(APIView):
    """
    Sends an email with a link to reset the password for the user
    """

    def post(self, request):
        """
        POST API -> /api/v1/user/password_reset/mail
        """

        serializer = PasswordResetMailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            random_string = get_random_string(30)
            key = 'password_reset:' + random_string
            cache_adapter_obj = CacheAdapter()
            cache_adapter_obj.set(
                key, email, EMAIL_EXPIRY_IN_SECONDS)
            link = get_domain_url(
                request) + reverse('user:password-reset', args=(random_string,))
            print(link)
            send_reset_password_email.delay(email, link)

            return Response({'response': 'Reset email sent!'},
                            status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
