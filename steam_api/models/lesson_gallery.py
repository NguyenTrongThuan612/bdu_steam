from django.db import models
from django.core.validators import MinValueValidator
from steam_api.models.course_module import CourseModule

class LessonGallery(models.Model):
    class Meta:
        db_table = "lesson_galleries"
        unique_together = ('module', 'lesson_number')
        ordering = ['lesson_number']
        
    id = models.BigAutoField(primary_key=True)
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='lesson_galleries')
    lesson_number = models.IntegerField(validators=[MinValueValidator(1)], help_text="The sequence number of the lesson in this module")
    image_urls = models.JSONField(default=list, help_text="List of image URLs for this lesson")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.module.class_room.name} - {self.module.name} - Lesson {self.lesson_number}"

    @property
    def images_count(self):
        return len(self.image_urls) 