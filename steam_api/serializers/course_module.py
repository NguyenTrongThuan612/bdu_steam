from rest_framework import serializers
from steam_api.models.course_module import CourseModule
from steam_api.models.lesson import Lesson

class CourseModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        fields = ['id', 'class_room', 'name', 'description', 'sequence_number', 'total_lessons', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class CreateCourseModuleSerializer(serializers.ModelSerializer):
    lesson_names = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True,
        required=False,
        help_text="List of lesson names for this module"
    )

    class Meta:
        model = CourseModule
        fields = ['class_room', 'name', 'description', 'sequence_number', 'total_lessons', 'lesson_names']

    def validate(self, data):
        # Call parent's validate method first
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
            # Update the automatically created lessons with custom names
            lessons = Lesson.objects.filter(module=instance).order_by('sequence_number')
            for lesson, name in zip(lessons, lesson_names):
                lesson.name = name
                lesson.save()
        
        return instance

class UpdateCourseModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        fields = ['name', 'description', 'total_lessons']

class ListCourseModuleSerializer(serializers.ModelSerializer):
    lesson_galleries_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseModule
        fields = ['id', 'name', 'sequence_number', 'total_lessons', 'lesson_galleries_count']
        
    def get_lesson_galleries_count(self, obj):
        return obj.lesson_galleries.count() 