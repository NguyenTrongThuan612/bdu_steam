from datetime import datetime
from django.db import models
from django.core.validators import MinValueValidator
from steam_api.models.course_module import CourseModule
from steam_api.helpers.lesson_schedule import calculate_lesson_status, get_lesson_start_datetime, get_lesson_end_datetime
from zoneinfo import ZoneInfo

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
        
    @property
    def status(self) -> str:
        class_room = self.module.class_room
        if not class_room.schedule:
            return 'not_started'
            
        previous_lessons = 0
        for module in class_room.modules.filter(
            sequence_number__lt=self.module.sequence_number,
            deleted_at__isnull=True
        ):
            previous_lessons += module.total_lessons
            
        absolute_sequence = previous_lessons + self.sequence_number
        
        return calculate_lesson_status(
            start_date=class_room.start_date,
            end_date=class_room.end_date,
            schedule=class_room.schedule,
            lesson_sequence=absolute_sequence
        )
    
    @property
    def start_datetime(self) -> datetime:
        replacement = self.replacements.filter(
            deleted_at__isnull=True
        ).order_by('schedule').first()
        
        if replacement:
            return replacement.schedule.astimezone(ZoneInfo('Asia/Ho_Chi_Minh'))
        
        return get_lesson_start_datetime(
            start_date=self.module.class_room.start_date,
            schedule=self.module.class_room.schedule,
            lesson_sequence=self.sequence_number
        )
    
    @property
    def end_datetime(self) -> datetime:      
        end_at = get_lesson_end_datetime(
            start_date=self.module.class_room.start_date,
            schedule=self.module.class_room.schedule,
            lesson_sequence=self.sequence_number
        )
        start_at = get_lesson_start_datetime(
            start_date=self.module.class_room.start_date,
            schedule=self.module.class_room.schedule,
            lesson_sequence=self.sequence_number
        )
        
        replacement = self.replacements.filter(
            lesson=self,
            deleted_at__isnull=True
        ).order_by('schedule').first()
        
        duration = end_at - start_at
        
        if replacement:
            return replacement.schedule.astimezone(ZoneInfo('Asia/Ho_Chi_Minh')) + duration
        
        return end_at