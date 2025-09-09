from django.db import models
from steam_api.models.lesson import Lesson

class LessonDocumentation(models.Model):
    class Meta:
        db_table = "lesson_documentations"

    id = models.BigAutoField(primary_key=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    link = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)