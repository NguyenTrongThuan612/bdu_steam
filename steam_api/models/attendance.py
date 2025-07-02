from django.db import models
from django.utils import timezone
from steam_api.models.student import Student
from steam_api.models.lesson import Lesson

class Attendance(models.Model):
    class Meta:
        db_table = "attendances"
        unique_together = ['student', 'lesson']
        ordering = ['-check_in_time']

    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]

    id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name='attendances'
    )
    lesson = models.ForeignKey(
        Lesson, 
        on_delete=models.CASCADE, 
        related_name='attendances'
    )
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='absent'
    )
    check_in_time = models.DateTimeField(null=True, blank=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.lesson.name} - {self.status}"

    def save(self, *args, **kwargs):
        if self.status == 'present' and not self.check_in_time:
            self.check_in_time = timezone.now()
        super().save(*args, **kwargs) 