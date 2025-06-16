from django.db import models
from steam_api.models.lesson import Lesson

class LessonGallery(models.Model):
    class Meta:
        db_table = "lesson_galleries"
        ordering = ['lesson__sequence_number']
        
    id = models.BigAutoField(primary_key=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='galleries')
    image_urls = models.JSONField(default=list, help_text="List of image URLs for this lesson")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.lesson.module.class_room.name} - {self.lesson.module.name} - Lesson {self.lesson.sequence_number}"

    @property
    def images_count(self):
        return len(self.image_urls) 