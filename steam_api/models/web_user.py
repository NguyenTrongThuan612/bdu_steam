from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager

class WebUserStatus(models.TextChoices):
    BLOCKED = "blocked"
    ACTIVATED = "activated"
    UNVERIFIED = "unverified"

class WebUserRole(models.TextChoices):
    ROOT = "root"
    MANAGER = "manager"
    TEACHER = "teacher"

class WebUser(AbstractBaseUser):
    class Meta:
        app_label = "steam_api"
        db_table = "web_users"

    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, null=False)
    phone = models.CharField(max_length=15)
    status = models.CharField(max_length=20, choices=WebUserStatus.choices)
    role = models.CharField(max_length=20, choices=WebUserRole.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = "email"

    objects = BaseUserManager()