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
        return StudentSerializer(obj.approved_students, many=True, context={'request': self.context.get('request')}).data
    
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