from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.contrib.auth.models import PermissionsMixin

class CommonInfo(models.Model):
    """
    Class containing common fields in all models.
    """
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def create_user(self, email, password,**kwargs):
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


    def create_superuser(self, email, password,**kwargs):
        """
        Creates and saves a superuser with the given email and password.
        """
        return self.create_user(email, password,**kwargs, is_admin=True, is_staff=True, is_superuser=True)


class User(AbstractBaseUser, PermissionsMixin, CommonInfo):
    """
    Class containing user model fields.
    """
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

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

    def save(self, *args, **kwargs):
        """
        Checks if user exists in database if not hashes user password and saves it.
        """
        if not self.id:
            self.set_password(self.password)
        return super(User, self).save(*args, **kwargs)
