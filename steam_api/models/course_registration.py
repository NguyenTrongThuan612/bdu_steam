from django.db import models
from django.utils import timezone
from steam_api.models.student import Student
from steam_api.models.class_room import ClassRoom

class CourseRegistration(models.Model):
    class Meta:
        db_table = "course_registrations"
        unique_together = ('student', 'class_room')
        
    id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='registrations')
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='registrations')
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('unpaid', 'Unpaid'),
            ('partially_paid', 'Partially Paid'),
            ('fully_paid', 'Fully Paid'),
        ],
        default='unpaid'
    )
    
    note = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.student.first_name} - {self.class_room.name} ({self.status})"
        
    def save(self, *args, **kwargs):
        if self.paid_amount >= self.amount:
            self.payment_status = 'fully_paid'
        elif self.paid_amount > 0:
            self.payment_status = 'partially_paid'
        else:
            self.payment_status = 'unpaid'
            
        super().save(*args, **kwargs) 