from datetime import datetime
from rest_framework import serializers
from steam_api.models.class_room import ClassRoom
from steam_api.serializers.student import StudentSerializer
from steam_api.serializers.web_user import WebUserSerializer
from steam_api.models.web_user import WebUser, WebUserRole, WebUserStatus
from steam_api.models.course import Course

class ClassRoomSerializer(serializers.ModelSerializer):
    teacher = WebUserSerializer(read_only=True)
    teaching_assistant = WebUserSerializer(read_only=True)
    students = serializers.SerializerMethodField()

    def get_students(self, obj):
        return StudentSerializer(obj.approved_students, many=True).data
    
    class Meta:
        model = ClassRoom
        fields = "__all__"

class CreateClassRoomSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=WebUser.objects.filter(role=WebUserRole.TEACHER, status=WebUserStatus.ACTIVATED),
        required=False,
        allow_null=True,
        default=None
    )
    teaching_assistant = serializers.PrimaryKeyRelatedField(
        queryset=WebUser.objects.filter(role=WebUserRole.TEACHER, status=WebUserStatus.ACTIVATED),
        required=False,
        allow_null=True,
        default=None
    )
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.filter(is_active=True, deleted_at__isnull=True)
    )
    
    class Meta:
        model = ClassRoom
        fields = ['name', 'description', 'course', 'teacher', 'teaching_assistant', 'max_students',
                 'start_date', 'end_date', 'schedule']
    
    def validate_schedule(self, value):
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        
        for k, v in value.items():
            if k.lower() not in days:
                raise serializers.ValidationError("Ngày học không hợp lệ!")
            
            time_range = v.split('-')
            if len(time_range) != 2:
                raise serializers.ValidationError("Giờ học không hợp lệ!")
            
            start_time = time_range[0]
            end_time = time_range[1]
            
            if datetime.strptime(start_time, '%H:%M').time() >= datetime.strptime(end_time, '%H:%M').time():
                raise serializers.ValidationError("Giờ học không hợp lệ!")
            
        return value

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
                 'max_students', 'start_date', 'end_date', 'schedule', 'is_active']
        extra_kwargs = {
            'name': {'required': False},
            'description': {'required': False},
            'max_students': {'required': False},
            'start_date': {'required': False},
            'end_date': {'required': False},
            'schedule': {'required': False},
            'is_active': {'required': False}
        }