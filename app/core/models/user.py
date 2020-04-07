from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin

from .base import BaseModel


class UserManager(BaseUserManager):

    def create_user(self, email, password, **extra_attributes):
        """
        Creates a saves a new user
        """
        if not email:
            raise ValueError('User should have email address')
        user = self.model(
            email=self.normalize_email(email),
            **extra_attributes)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """
        Creates a super user
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    Custom user model that supports using email instead of username
    """
    email = models.EmailField(max_length=255, null=False, unique=True)
    name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15, null=False, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
