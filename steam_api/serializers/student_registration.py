from rest_framework import serializers
from steam_api.models.student import Student
from steam_api.models.student_registration import StudentRegistration, StudentRegistrationStatus
from steam_api.serializers.app_user import AppUserSerializer

class StudentRegistrationSerializer(serializers.ModelSerializer):
    app_user = AppUserSerializer(read_only=True)
    
    class Meta:
        model = StudentRegistration
        fields = '__all__'
        read_only_fields = ['status', 'note', 'created_at', 'updated_at', 'deleted_at']

class CreateStudentRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    date_of_birth = serializers.DateField(required=True)
    identification_number = serializers.CharField(required=True)

    def validate(self, attrs):
        _attrs = super().validate(attrs)
        if not Student.objects.filter(
            first_name=_attrs['first_name'],
            last_name=_attrs['last_name'],
            date_of_birth=_attrs['date_of_birth'],
            identification_number=_attrs['identification_number']
        ).exists():
            raise serializers.ValidationError("Student not found.")
        
        return _attrs

class UpdateStudentRegistrationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentRegistration
        fields = ['status', 'note']
        extra_kwargs = {
            'status': {'required': True},
            'note': {'required': False}
        }

    def validate_status(self, value):
        if value not in [StudentRegistrationStatus.APPROVED, StudentRegistrationStatus.REJECTED]:
            raise serializers.ValidationError("Status must be either approved or rejected")
        return value 