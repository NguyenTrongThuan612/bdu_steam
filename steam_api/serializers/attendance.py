from rest_framework import serializers
from steam_api.models.attendance import Attendance
from steam_api.models.course_registration import CourseRegistration
from steam_api.serializers.student import StudentSerializer
from steam_api.serializers.lesson import LessonSerializer

class AttendanceSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    lesson = LessonSerializer(read_only=True)
    
    class Meta:
        model = Attendance
        fields = "__all__"

class CreateAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['student', 'lesson', 'status', 'note']

    def validate(self, data):
        if Attendance.objects.filter(
            student=data['student'],
            lesson=data['lesson'],
            deleted_at__isnull=True
        ).exists():
            raise serializers.ValidationError("Attendance record already exists for this student and lesson")

        class_room = data['lesson'].module.class_room
        registration = CourseRegistration.objects.filter(
            student=data['student'],
            class_room=class_room,
            status='approved',
            deleted_at__isnull=True
        ).first()

        if not registration:
            raise serializers.ValidationError(
                "Student is not registered for this class or registration is not approved/fully paid"
            )

        return data 