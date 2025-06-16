from django.db import models
from django.core.validators import MinValueValidator
from steam_api.models.course_module import CourseModule

class Lesson(models.Model):
    class Meta:
        db_table = "lessons"
        ordering = ['sequence_number']
        unique_together = ('module', 'sequence_number')
        
    id = models.BigAutoField(primary_key=True)
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='lessons')
    name = models.CharField(max_length=255, help_text="Custom name for this lesson")
    sequence_number = models.IntegerField(
        validators=[MinValueValidator(1)], 
        help_text="The sequence number of this lesson in the module"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.module.class_room.name} - {self.module.name} - {self.name} (Lesson {self.sequence_number})" 