from rest_framework import serializers
from steam_api.models.course_registration import CourseRegistration
from steam_api.serializers.student import StudentSerializer
from steam_api.serializers.class_room import ClassRoomSerializer
from steam_api.models.student import Student
from steam_api.models.class_room import ClassRoom

class CourseRegistrationSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    class_room = ClassRoomSerializer(read_only=True)
    
    def get_student(self, obj):
        return StudentSerializer(obj.student).data
    
    class Meta:
        model = CourseRegistration
        fields = "__all__"

class AnonymousContact(serializers.Serializer):
    student_name = serializers.CharField(required=True)
    parent_name = serializers.CharField(required=True)
    parent_phone = serializers.CharField(required=True)
    parent_email = serializers.EmailField(required=True)

class CreateCourseRegistrationSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=Student.objects.filter(deleted_at__isnull=True),
        allow_null=True
    )
    class_room = serializers.PrimaryKeyRelatedField(
        queryset=ClassRoom.objects.filter(is_active=True, deleted_at__isnull=True)
    )
    contact_for_anonymous = AnonymousContact(required=False, allow_null=True)
    
    class Meta:
        model = CourseRegistration
        fields = ['student', 'class_room', 'note', 'amount', 'contact_for_anonymous']
        
    def validate(self, data):
        data = super().validate(data)

        if not self.context.get("allow_anonymous", False) and data['student'] is None:
            raise serializers.ValidationError("Student is required")
        
        elif self.context.get("allow_anonymous", False) and data['contact_for_anonymous'] is None:
            raise serializers.ValidationError("Student or contact_for_anonymous is required")
        
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