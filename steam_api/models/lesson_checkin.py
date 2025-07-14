from django.db import models
from django.utils import timezone
from steam_api.models.lesson import Lesson
from steam_api.models.web_user import WebUser

class LessonCheckinType(models.TextChoices):
    TEACHER = 'teacher', 'Teacher'
    TEACHING_ASSISTANT = 'teaching_assistant', 'Teaching Assistant'

class LessonCheckin(models.Model):
    class Meta:
        db_table = "lesson_checkins"
        unique_together = ('lesson', 'user')
        
    id = models.BigAutoField(primary_key=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='checkins')
    user = models.ForeignKey(WebUser, on_delete=models.CASCADE, related_name='lesson_checkins')
    checkin_type = models.CharField(
        max_length=20,
        choices=LessonCheckinType.choices,
        help_text="Type of user checking in (teacher or teaching assistant)"
    )
    checkin_time = models.DateTimeField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.lesson} - {self.user.full_name} ({self.checkin_type})"