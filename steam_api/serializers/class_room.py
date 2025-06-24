from rest_framework import serializers
from steam_api.models.class_room import ClassRoom
from steam_api.serializers.web_user import WebUserSerializer
from steam_api.models.web_user import WebUser, WebUserRole, WebUserStatus
from steam_api.models.course import Course

class ClassRoomSerializer(serializers.ModelSerializer):
    teacher = WebUserSerializer(read_only=True)
    teaching_assistant = WebUserSerializer(read_only=True)
    
    class Meta:
        model = ClassRoom
        fields = ['id', 'name', 'description', 'thumbnail_url', 'course', 'teacher', 'teaching_assistant',
                 'max_students', 'start_date', 'end_date', 'schedule', 'total_sessions', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'thumbnail_url']

class CreateClassRoomSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=WebUser.objects.filter(role=WebUserRole.TEACHER, status=WebUserStatus.ACTIVATED),
        required=False,
        allow_null=True
    )
    teaching_assistant = serializers.PrimaryKeyRelatedField(
        queryset=WebUser.objects.filter(role=WebUserRole.TEACHER, status=WebUserStatus.ACTIVATED),
        required=False,
        allow_null=True
    )
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.filter(is_active=True, deleted_at__isnull=True)
    )
    
    class Meta:
        model = ClassRoom
        fields = ['name', 'description', 'course', 'teacher', 'teaching_assistant', 'max_students',
                 'start_date', 'end_date', 'schedule', 'total_sessions']

    def validate(self, data):
        data = super().validate(data)
        
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError({'end_date': 'End date must be after start date'})
        
        if 'teaching_assistant' in data and 'teacher' in data:
            if data['teaching_assistant'] and data['teacher'] and data['teaching_assistant'] == data['teacher']:
                raise serializers.ValidationError({'teaching_assistant': 'Teacher and teaching assistant cannot be the same person'})

        if 'total_sessions' in data and data['total_sessions'] < 0:
            raise serializers.ValidationError({'total_sessions': 'Total sessions cannot be negative'})
            
        return data

class UpdateClassRoomSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=WebUser.objects.filter(role=WebUserRole.TEACHER, status=WebUserStatus.ACTIVATED),
        required=False,
        allow_null=True
    )
    teaching_assistant = serializers.PrimaryKeyRelatedField(
        queryset=WebUser.objects.filter(role=WebUserRole.TEACHER, status=WebUserStatus.ACTIVATED),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = ClassRoom
        fields = ['name', 'description', 'teacher', 'teaching_assistant',
                 'max_students', 'start_date', 'end_date', 'schedule', 'total_sessions', 'is_active']
        extra_kwargs = {
            'name': {'required': False},
            'description': {'required': False},
            'max_students': {'required': False},
            'start_date': {'required': False},
            'end_date': {'required': False},
            'schedule': {'required': False},
            'total_sessions': {'required': False},
            'is_active': {'required': False}
        }

    def validate(self, data):
        data = super().validate(data)
        
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError({'end_date': 'End date must be after start date'})
        elif 'start_date' in data and self.instance:
            if data['start_date'] > self.instance.end_date:
                raise serializers.ValidationError({'start_date': 'Start date cannot be after current end date'})
        elif 'end_date' in data and self.instance:
            if self.instance.start_date > data['end_date']:
                raise serializers.ValidationError({'end_date': 'End date cannot be before current start date'})
                
        # Check if teacher and teaching assistant are the same person
        teacher = data.get('teacher', self.instance.teacher if self.instance else None)
        assistant = data.get('teaching_assistant', self.instance.teaching_assistant if self.instance else None)
        if teacher and assistant and teacher == assistant:
            raise serializers.ValidationError({'teaching_assistant': 'Teacher and teaching assistant cannot be the same person'})

        if 'total_sessions' in data and data['total_sessions'] < 0:
            raise serializers.ValidationError({'total_sessions': 'Total sessions cannot be negative'})
            
        return data

class ListClassRoomSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    assistant_name = serializers.CharField(source='teaching_assistant.full_name', read_only=True)
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ClassRoom
        fields = ['id', 'name', 'total_sessions', 'start_date', 'teacher_name', 'assistant_name', 'student_count']
        
    def get_student_count(self, obj):
        return obj.students.count() if hasattr(obj, 'students') else 0 