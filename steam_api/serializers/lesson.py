from rest_framework import serializers
from django.db import models, transaction
from steam_api.models.lesson import Lesson
from steam_api.models.course_module import CourseModule
from steam_api.models.lesson_evaluation import LessonEvaluation

class LessonSerializer(serializers.ModelSerializer):
    is_evaluated = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField(
        help_text="Status of the lesson: 'not_started', 'in_progress', or 'completed'"
    )
    start_datetime = serializers.SerializerMethodField()
    end_datetime = serializers.SerializerMethodField()
    schedule = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = "__all__"
        
    def get_is_evaluated(self, obj):
        student_id = self.context.get('student_id')
        
        if not student_id:
            return None
            
        return LessonEvaluation.objects.filter(
            lesson=obj,
            student_id=student_id,
            deleted_at__isnull=True
        ).exists()
        
    def get_status(self, obj):
        return obj.status

    def get_start_datetime(self, obj: Lesson):
        return obj.start_datetime
    
    def get_end_datetime(self, obj: Lesson):
        return obj.end_datetime
    
    def get_schedule(self, obj: Lesson):
        return {
            "start_date": obj.start_datetime.strftime("%d/%m/%Y"),
            "start_time": obj.start_datetime.strftime("%H:%M"),
            "end_date": obj.end_datetime.strftime("%d/%m/%Y"),
            "end_time": obj.end_datetime.strftime("%H:%M"),
            "duration": (obj.end_datetime - obj.start_datetime).total_seconds() / 60,
            "status": obj.status,
            "name": obj.name,
        }
    
class UpdateLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['name']

class CreateLessonSerializer(serializers.ModelSerializer):
    module = serializers.PrimaryKeyRelatedField(
        queryset=CourseModule.objects.filter(deleted_at__isnull=True)
    )
    
    class Meta:
        model = Lesson
        fields = ['module', 'name', 'sequence_number']

    def validate(self, data):
        data = super().validate(data)
        
        sequence_number = data['sequence_number']

        if sequence_number <= 0:
            raise serializers.ValidationError({
                'sequence_number': 'Sequence number must be greater than 0'
            })

        return data

    @transaction.atomic
    def create(self, validated_data):
        module = validated_data['module']
        sequence_number = validated_data['sequence_number']

        Lesson.objects.filter(
            module=module,
            sequence_number__gte=sequence_number,
            deleted_at__isnull=True
        ).order_by('-sequence_number').update(sequence_number=models.F('sequence_number') + 1)

        lesson = super().create(validated_data)

        module.total_lessons += 1
        module.save(update_fields=['total_lessons'])

        return lesson 