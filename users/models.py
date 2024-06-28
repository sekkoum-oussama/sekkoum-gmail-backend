from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from users.users_manager import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, blank=False, null=False)
    username = models.CharField(max_length=100, blank=False, null=False, unique=True)
    photo = models.ImageField()
    date_joined = models.DateField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self) -> str:
        return self.email