from django.conf import settings
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token

from utils import (
    models as util_models,
    managers as util_managers,
)


class UserManager(BaseUserManager, util_managers.SoftDeletionManager):
    """
    Custom Manager for User.
    """
    def create(self, email, password, **kwargs):
        """
        Creates and saves a user with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            **kwargs
        )
        user.set_password(password)

        try:
            previous_user = User.all_objects.get(email=email)
            previous_user.hard_delete()
        except User.DoesNotExist:
            pass
            
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        """
        Creates and saves a superuser with the given email and password.
        """
        return self.create(email=email, password=password, **kwargs, is_admin=True, is_staff=True, is_superuser=True)


class User(AbstractBaseUser, PermissionsMixin, util_models.CommonInfo, util_models.SoftDeletionModel):
    """
    Class containing user model fields.
    """
    email = models.EmailField(max_length=255, unique=True, help_text='Email Address')
    first_name = models.CharField(max_length=50, help_text='First Name of User')
    last_name = models.CharField(max_length=50, null=True, blank=True, help_text='Last Name of User')
    is_admin = models.BooleanField(
        default=False, help_text='This user has all permissions without explicitly assigning them'
    )
    is_staff = models.BooleanField(default=False, help_text='This user can access admin panel')
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

    @property
    def token(self):
        token, _ = Token.objects.get_or_create(user=self)
        return token
