from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import UserManager
from .role import StaffRole
from core.common.models.base import BaseModel

class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    role = models.CharField(
        max_length=20, 
        choices=StaffRole.choices, 
        default=None, 
        null=True, 
        blank=True
    )
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    
    # created_at and updated_at are now inherited from BaseModel

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.email
