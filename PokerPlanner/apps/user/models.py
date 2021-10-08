from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)

from utils import models as util_models
from utils import managers as util_managers


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
    first_name = models.CharField(max_length=50, null=False, help_text='First Name of User')
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

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
