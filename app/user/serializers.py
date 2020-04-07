from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from helpers.validators import is_valid_email, is_strong_password, is_valid_mobile_number


class UserSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, max_length=255)
    password = serializers.CharField(required=True, max_length=255)
    confirm_password = serializers.CharField(required=True, max_length=255)
    name = serializers.CharField(required=True, max_length=255)
    mobile_number = serializers.CharField(required=True, max_length=15)
    uuid = serializers.UUIDField(required=False)

    def does_user_exist(self, **param):
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
