from rest_framework import serializers
from steam_api.models.course import Course
from steam_api.helpers.firebase_storage import upload_image_to_firebase

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'thumbnail_url', 'price', 'duration', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class CreateCourseSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(write_only=True, required=False)
    
    class Meta:
        model = Course
        fields = ['name', 'description', 'thumbnail', 'price', 'duration']

    def create(self, validated_data):
        thumbnail = validated_data.pop('thumbnail', None)
        
        if thumbnail:
            try:
                thumbnail_url = upload_image_to_firebase(thumbnail)
                validated_data['thumbnail_url'] = thumbnail_url
            except Exception as e:
                raise serializers.ValidationError({'thumbnail': str(e)})
                
        return super().create(validated_data)

class UpdateCourseSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(write_only=True, required=False)
    
    class Meta:
        model = Course
        fields = ['name', 'description', 'thumbnail', 'price', 'duration', 'is_active']
        extra_kwargs = {
            'name': {'required': False},
            'description': {'required': False},
            'price': {'required': False},
            'duration': {'required': False},
            'is_active': {'required': False}
        }

    def update(self, instance, validated_data):
        thumbnail = validated_data.pop('thumbnail', None)
        
        if thumbnail:
            try:
                thumbnail_url = upload_image_to_firebase(thumbnail)
                validated_data['thumbnail_url'] = thumbnail_url
            except Exception as e:
                raise serializers.ValidationError({'thumbnail': str(e)})
                
        return super().update(instance, validated_data) 