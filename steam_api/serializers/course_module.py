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
