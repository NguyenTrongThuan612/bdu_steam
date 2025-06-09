from rest_framework import serializers
from steam_api.models.course_module import CourseModule

class CourseModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        fields = ['id', 'class_room', 'name', 'description', 'sequence_number', 'total_lessons', 'created_at']
        read_only_fields = ['id', 'created_at']

class CreateCourseModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        fields = ['class_room', 'name', 'description', 'sequence_number', 'total_lessons']
        
    def validate(self, data):
        # Kiểm tra sequence_number không trùng với module khác trong cùng lớp
        try:
            existing_module = CourseModule.objects.get(
                class_room=data['class_room'],
                sequence_number=data['sequence_number'],
                deleted_at__isnull=True
            )
            raise serializers.ValidationError(
                f"Module with sequence number {data['sequence_number']} already exists in this class"
            )
        except CourseModule.DoesNotExist:
            pass
            
        return data

class UpdateCourseModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        fields = ['name', 'description', 'sequence_number', 'total_lessons']
        extra_kwargs = {
            'name': {'required': False},
            'description': {'required': False},
            'sequence_number': {'required': False},
            'total_lessons': {'required': False}
        }
        
    def validate(self, data):
        if 'sequence_number' in data:
            # Kiểm tra sequence_number không trùng với module khác trong cùng lớp
            try:
                existing_module = CourseModule.objects.get(
                    class_room=self.instance.class_room,
                    sequence_number=data['sequence_number'],
                    deleted_at__isnull=True
                )
                if existing_module.id != self.instance.id:
                    raise serializers.ValidationError(
                        f"Module with sequence number {data['sequence_number']} already exists in this class"
                    )
            except CourseModule.DoesNotExist:
                pass
                
        return data

class ListCourseModuleSerializer(serializers.ModelSerializer):
    lesson_galleries_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseModule
        fields = ['id', 'name', 'sequence_number', 'total_lessons', 'lesson_galleries_count']
        
    def get_lesson_galleries_count(self, obj):
        return obj.lesson_galleries.count() 