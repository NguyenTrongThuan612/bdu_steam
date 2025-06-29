from rest_framework import serializers
from steam_api.models.student_registration_request import StudentRegistrationRequest, StudentRegistrationRequestStatus
from steam_api.serializers.app_user import AppUserSerializer

class StudentRegistrationRequestSerializer(serializers.ModelSerializer):
    app_user = AppUserSerializer(read_only=True)
    
    class Meta:
        model = StudentRegistrationRequest
        fields = '__all__'
        read_only_fields = ['status', 'note', 'created_at', 'updated_at', 'deleted_at']

class CreateStudentRegistrationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentRegistrationRequest
        fields = ['first_name', 'last_name', 'date_of_birth', 'identification_number']

    def validate_identification_number(self, value):
        request = self.context.get('request')
        if request and StudentRegistrationRequest.objects.filter(
            app_user=request.user,
            identification_number=value,
            status=StudentRegistrationRequestStatus.PENDING
        ).exists():
            raise serializers.ValidationError("A pending request with this identification number already exists.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if request:
            validated_data['app_user'] = request.user
        return super().create(validated_data)

class UpdateStudentRegistrationRequestStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentRegistrationRequest
        fields = ['status', 'note']
        extra_kwargs = {
            'status': {'required': True},
            'note': {'required': False}
        }

    def validate_status(self, value):
        if value not in [StudentRegistrationRequestStatus.APPROVED, StudentRegistrationRequestStatus.REJECTED]:
            raise serializers.ValidationError("Status must be either approved or rejected")
        return value 