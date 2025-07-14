from django.db import models
from django.utils import timezone
from steam_api.models.course import Course
from steam_api.models.web_user import WebUser
from steam_api.models.student import Student

class ClassRoom(models.Model):
    class Meta:
        db_table = "class_rooms"
        
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    thumbnail_url = models.CharField(max_length=500, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='classes')
    teacher = models.ForeignKey(WebUser, on_delete=models.SET_NULL, null=True, related_name='teaching_classes')
    teaching_assistant = models.ForeignKey(WebUser, on_delete=models.SET_NULL, null=True, related_name='assisting_classes')
    max_students = models.IntegerField(default=20)
    start_date = models.DateField()
    end_date = models.DateField()
    schedule = models.JSONField(help_text="Weekly schedule in JSON format", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    @property
    def total_sessions(self):
        return sum(module.total_lessons for module in self.modules.filter(deleted_at__isnull=True))

    @property
    def approved_students(self):
        return Student.objects.filter(
            registrations__class_room=self,
            registrations__status='approved',
            registrations__deleted_at__isnull=True,
            is_active=True,
            deleted_at__isnull=True
        )

    @property
    def current_students_count(self):
        return self.approved_students.count()

    @property
    def available_slots(self):
        return max(0, self.max_students - self.current_students_count) 