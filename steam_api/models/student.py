from django.db import models
from django.utils import timezone

class Student(models.Model):
    class Meta:
        db_table = "students"
        
    id = models.AutoField(primary_key=True)
    identification_number = models.CharField(max_length=20, unique=True, help_text="Birth certificate number or identification number")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    parent_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=15)
    parent_email = models.EmailField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    avatar_url = models.CharField(max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.identification_number})" 