from rest_framework import serializers
from steam_api.models.course_module import CourseModule
from steam_api.models.lesson import Lesson
from steam_api.models.class_room import ClassRoom

class CourseModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        fields = "__all__"

class CreateCourseModuleSerializer(serializers.ModelSerializer):
    lesson_names = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True,
        required=False,
        help_text="List of lesson names for this module"
    )
    class_room = serializers.PrimaryKeyRelatedField(
        queryset=ClassRoom.objects.filter(is_active=True, deleted_at__isnull=True)
    )

    class Meta:
        model = CourseModule
        fields = ['class_room', 'name', 'description', 'sequence_number', 'total_lessons', 'lesson_names']

    def validate(self, data):
        data = super().validate(data)
        
        if 'lesson_names' in data:
            if len(data['lesson_names']) != data['total_lessons']:
                raise serializers.ValidationError({
                    'lesson_names': f"Number of lesson names ({len(data['lesson_names'])}) must match total_lessons ({data['total_lessons']})"
                })
        return data

    def create(self, validated_data):
        lesson_names = validated_data.pop('lesson_names', None)
        instance = super().create(validated_data)
        
        if lesson_names:
            lessons = Lesson.objects.filter(module=instance).order_by('sequence_number')
            for lesson, name in zip(lessons, lesson_names):
                lesson.name = name
                lesson.save()
        
        return instance

class UpdateCourseModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        fields = ['name', 'description', 'total_lessons']
