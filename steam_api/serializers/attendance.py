from rest_framework import serializers
from steam_api.models.attendance import Attendance
from steam_api.serializers.student import StudentSerializer
from steam_api.serializers.lesson import LessonSerializer

class AttendanceSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    lesson = LessonSerializer(read_only=True)

    def get_student(self, obj):
        return StudentSerializer(obj.student, context={'request': self.context.get('request')}).data
    
    class Meta:
        model = Attendance
        fields = "__all__"

class CreateAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['student', 'lesson', 'status', 'note']