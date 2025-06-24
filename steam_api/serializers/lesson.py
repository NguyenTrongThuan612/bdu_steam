from rest_framework import serializers
from django.db import models, transaction
from steam_api.models.lesson import Lesson
from steam_api.models.course_module import CourseModule

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"

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
        
        module = data['module']
        sequence_number = data['sequence_number']

        if sequence_number <= 0:
            raise serializers.ValidationError({
                'sequence_number': 'Sequence number must be greater than 0'
            })

        max_allowed = module.total_lessons + 1
        if sequence_number > max_allowed:
            raise serializers.ValidationError({
                'sequence_number': f'Sequence number cannot be greater than {max_allowed}'
            })

        if Lesson.objects.filter(
            module=module,
            sequence_number=sequence_number,
            deleted_at__isnull=True
        ).exists():
            raise serializers.ValidationError({
                'sequence_number': f'Lesson with sequence number {sequence_number} already exists in this module'
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