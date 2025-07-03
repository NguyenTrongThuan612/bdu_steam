from django.db import models
from steam_api.models.app_user import AppUser
from steam_api.models.student import Student

class StudentRegistrationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"

class StudentRegistration(models.Model):
    class Meta:
        db_table = "student_registrations"
        unique_together = ['app_user', 'student']
        
    id = models.BigAutoField(primary_key=True)
    app_user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='student_registrations')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_registrations')
    status = models.CharField(
        max_length=20, 
        choices=StudentRegistrationStatus.choices,
        default=StudentRegistrationStatus.PENDING
    )
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True) 