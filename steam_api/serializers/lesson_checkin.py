from datetime import datetime
from rest_framework import serializers
from steam_api.models.lesson import Lesson
from steam_api.models.lesson_checkin import LessonCheckin
from steam_api.models.web_user import WebUser, WebUserRole, WebUserStatus
from steam_api.serializers.web_user import WebUserSerializer
from steam_api.serializers.lesson import LessonSerializer

class LessonCheckinSerializer(serializers.ModelSerializer):
    user = WebUserSerializer(read_only=True)
    lesson = LessonSerializer(read_only=True)
    
    class Meta:
        model = LessonCheckin
        fields = "__all__"

class LessonCheckinCreateSerializer(serializers.ModelSerializer):
    lesson = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.filter(deleted_at__isnull=True), required=True)

    class Meta:
        model = LessonCheckin
        fields = ['lesson']

    def validate(self, data):
        _data = super().validate(data)
        user = self.context.get('user', None)
        
        if not user:
            raise serializers.ValidationError("User is required")
        
        _data['user'] = user

        if _data['lesson'].module.class_room.teacher_id == user.id:
            _data['checkin_type'] = 'teacher'
        else:
            _data['checkin_type'] = 'teaching_assistant'

        _data['checkin_time'] = self.context.get('checkin_time', datetime.now())

        return _data