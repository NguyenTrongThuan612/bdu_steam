from rest_framework import serializers
from steam_api.models.course_registration import CourseRegistration
from steam_api.serializers.student import StudentSerializer
from steam_api.serializers.class_room import ClassRoomSerializer
from steam_api.models.student import Student
from steam_api.models.class_room import ClassRoom

class CourseRegistrationSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    class_room = ClassRoomSerializer(read_only=True)
    
    class Meta:
        model = CourseRegistration
        fields = "__all__"

class CreateCourseRegistrationSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.filter(deleted_at__isnull=True)
    )
    class_room = serializers.PrimaryKeyRelatedField(
        queryset=ClassRoom.objects.filter(is_active=True, deleted_at__isnull=True)
    )
    
    class Meta:
        model = CourseRegistration
        fields = ['student', 'class_room', 'note', 'amount']
        
    def validate(self, data):
        data = super().validate(data)
        data['amount'] = data['class_room'].course.price
        return data

class UpdateCourseRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseRegistration
        fields = ['status', 'paid_amount', 'payment_method', 'note']
        extra_kwargs = {
            'status': {'required': False},
            'paid_amount': {'required': False},
            'payment_method': {'required': False},
            'note': {'required': False}
        }