from django.db import models
from django.db.models import Q
from steam_api.models.lesson import Lesson

class LessonReplacement(models.Model):
    class Meta:
        db_table = "lesson_replacements"

    id = models.BigAutoField(primary_key=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='replacements')
    schedule = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True)