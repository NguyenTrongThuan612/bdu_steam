from django.db import models
from steam_api.models.app_user import AppUser

class StudentRegistrationRequestStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"

class StudentRegistrationRequest(models.Model):
    class Meta:
        db_table = "student_registration_requests"
        unique_together = ['app_user', 'identification_number']
        
    id = models.BigAutoField(primary_key=True)
    app_user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='registration_requests')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    identification_number = models.CharField(max_length=20, help_text="Birth certificate number or identification number")
    status = models.CharField(
        max_length=20, 
        choices=StudentRegistrationRequestStatus.choices,
        default=StudentRegistrationRequestStatus.PENDING
    )
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True) 