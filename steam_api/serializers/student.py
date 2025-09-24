from rest_framework import serializers
from steam_api.models.student import Student
from steam_api.helpers.local_storage import upload_file_to_local

class StudentSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    def get_avatar_url(self, obj):
        return self.context.get('request').build_absolute_uri(obj.avatar_url)

    class Meta:
        model = Student
        fields = "__all__"

class CreateStudentSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(write_only=True, required=False)
    
    class Meta:
        model = Student
        fields = [
            'identification_number', 'first_name', 'last_name',
            'date_of_birth', 'gender', 'address', 'phone_number', 'email',
            'parent_name', 'parent_phone', 'parent_email', 'note', 'avatar'
        ]

    def validate_identification_number(self, value):
        if Student.objects.filter(identification_number=value).exists():
            raise serializers.ValidationError("A student with this identification number already exists.")
        return value

    def create(self, validated_data):
        avatar = validated_data.pop('avatar', None)
        
        if avatar:
            try:
                avatar_url = upload_file_to_local(avatar)
                validated_data['avatar_url'] = avatar_url
            except Exception as e:
                raise serializers.ValidationError({'avatar': str(e)})
                
        return super().create(validated_data)

class UpdateStudentSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(write_only=True, required=False)
    
    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'address', 'phone_number', 'email', 'parent_name',
            'parent_phone', 'parent_email', 'note', 'avatar', 'is_active'
        ]
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'date_of_birth': {'required': False},
            'gender': {'required': False},
            'parent_name': {'required': False},
            'parent_phone': {'required': False},
            'is_active': {'required': False}
        }

    def update(self, instance, validated_data):
        avatar = validated_data.pop('avatar', None)
        
        if avatar:
            try:
                avatar_url = upload_file_to_local(avatar)
                validated_data['avatar_url'] = avatar_url
            except Exception as e:
                raise serializers.ValidationError({'avatar': str(e)})
                
        return super().update(instance, validated_data) 