from django.db import models
from django.core.validators import MinValueValidator
from steam_api.models.class_room import ClassRoom

class CourseModule(models.Model):
    class Meta:
        db_table = "course_modules"
        ordering = ['sequence_number']
        unique_together = ('class_room', 'sequence_number')
        
    id = models.BigAutoField(primary_key=True)
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='modules')
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    sequence_number = models.IntegerField(validators=[MinValueValidator(1)], help_text="The order of this module in the class")
    total_lessons = models.IntegerField(validators=[MinValueValidator(1)], help_text="Total number of lessons in this module")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.class_room.name} - {self.name} (Module {self.sequence_number})" 