from rest_framework import serializers
from django.http import Http404
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ObjectDoesNotExist

from helpers.cache_adapter import CacheAdapter
from helpers.validators import is_valid_email, is_strong_password, is_valid_mobile_number
from .constants import *


class RegisterUserSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, max_length=255)
    password = serializers.CharField(required=True, max_length=255)
    confirm_password = serializers.CharField(required=True, max_length=255)
    name = serializers.CharField(required=True, max_length=255)
    mobile_number = serializers.CharField(required=True, max_length=15)
    uuid = serializers.UUIDField(required=False)

    def does_user_exist(self, **param):
        """
        Checks if user exist in the system
        Returns Boolean
        """
        try:
            get_user_model().objects.get(**param)

            return True
        except ObjectDoesNotExist:
            return False

    def validate(self, attrs):
        """
        Validate the body params
        """
        email = attrs.get('email')
        mobile_number = attrs.get('mobile_number')

        errors = {}
        if is_valid_email(email) == False:
            errors['email'] = ["Not a valid email"]

        if self.does_user_exist(email=email):
            errors['email'] = ["User with this email already exist"]

        if is_strong_password(attrs.get('password')) == False:
            errors['password'] = ["Not a strong password"]

        if is_valid_mobile_number(attrs.get('mobile_number')) == False:
            errors['mobile_number'] = ["Not a valid mobile number"]

        if self.does_user_exist(mobile_number=mobile_number):
            errors['mobile_number'] = [
                "User with this mobile number already exist"]

        if attrs.get('password') != attrs.get('confirm_password'):
            errors['confirm_password'] = ["Passwords do not match."]

        if errors == {}:
            return attrs
        else:
            raise serializers.ValidationError(errors)

    def create(self, validated_data):
        """
        Creates the user in core_user table
        """
        validated_data.pop('confirm_password')

        return get_user_model().objects.create_user(**validated_data)


class EmailLoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, max_length=255)
    password = serializers.CharField(required=True, max_length=255)
    user = serializers.CharField(required=False)

    def validate(self, attrs):
        """
        Validates the email id and password
        """
        email = attrs.get('email')
        try:
            get_user_model().objects.get(email=email)
        except ObjectDoesNotExist:
            raise Http404

        user = authenticate(
            request=self.context.get('request'),
            username=attrs.get('email'),
            password=attrs.get('password')
        )

        if not user:
            raise serializers.ValidationError(
                {'auth_failure': 'Unable to authenticate with provided credential'},
                code='authentication'
            )

        return attrs


class OTPLoginSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(required=True, max_length=15)
    otp = serializers.CharField(required=True)

    def validate(self, attrs):
        """
        Validates if the OTP is correct for a given
        mobile number
        """
        mobile_number = attrs.get('mobile_number')
        try:
            get_user_model().objects.get(mobile_number=mobile_number)
        except ObjectDoesNotExist:
            raise Http404

        key = OTP_PREFIX + mobile_number
        param_otp = attrs.get('otp')
        cache_adapter_obj = CacheAdapter()
        cached_otp_value = cache_adapter_obj.get(key)
        user = None
        if param_otp == cached_otp_value:
            user = get_user_model().objects.get(mobile_number=mobile_number)

        if not user:
            raise serializers.ValidationError(
                {'auth_failure': 'Unable to authenticate with provided credential'},
                code='authentication'
            )

        return attrs


class OTPGenerateSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(required=True, max_length=15)

    def validate(self, attrs):
        """
        Validates if the mobile number for which OTP needs
        to be sent exists in the system
        """
        mobile_number = attrs.get('mobile_number')
        try:
            user = get_user_model().objects.get(mobile_number=mobile_number)
        except ObjectDoesNotExist:
            raise Http404

        return attrs
