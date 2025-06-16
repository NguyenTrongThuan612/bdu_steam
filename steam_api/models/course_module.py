from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
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
        
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        old_total_lessons = None
        
        if not is_new:
            try:
                old_instance = CourseModule.objects.get(pk=self.pk)
                old_total_lessons = old_instance.total_lessons
            except CourseModule.DoesNotExist:
                pass
                
        # Save the module first
        super().save(*args, **kwargs)
        
        # Import here to avoid circular import
        from steam_api.models.lesson import Lesson
        
        if is_new:
            # Create lessons for new module with default names
            lessons_to_create = []
            for i in range(1, self.total_lessons + 1):
                lessons_to_create.append(Lesson(
                    module=self,
                    sequence_number=i,
                    name=f"Lesson {i}"  # Default name if not provided
                ))
            Lesson.objects.bulk_create(lessons_to_create)
        elif old_total_lessons is not None and old_total_lessons != self.total_lessons:
            # Update lessons when total_lessons changes
            if self.total_lessons > old_total_lessons:
                # Add new lessons
                lessons_to_create = []
                for i in range(old_total_lessons + 1, self.total_lessons + 1):
                    lessons_to_create.append(Lesson(
                        module=self,
                        sequence_number=i,
                        name=f"Lesson {i}"  # Default name for new lessons
                    ))
                Lesson.objects.bulk_create(lessons_to_create)
            else:
                # Mark excess lessons as deleted
                Lesson.objects.filter(
                    module=self,
                    sequence_number__gt=self.total_lessons,
                    deleted_at__isnull=True
                ).update(deleted_at=timezone.now())
                
    def delete(self, *args, **kwargs):
        # Soft delete all related lessons
        from steam_api.models.lesson import Lesson
        Lesson.objects.filter(module=self, deleted_at__isnull=True).update(deleted_at=timezone.now())
        
        # Soft delete the module
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at']) 