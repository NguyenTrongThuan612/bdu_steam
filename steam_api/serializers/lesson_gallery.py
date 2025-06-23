from rest_framework import serializers
from steam_api.models.lesson_gallery import LessonGallery
from steam_api.helpers.firebase_storage import upload_image_to_firebase
from steam_api.models.lesson import Lesson

class LessonGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonGallery
        fields = ['id', 'lesson', 'image_urls', 'created_at']
        read_only_fields = ['id', 'created_at']

class CreateLessonGallerySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True)
    lesson = serializers.PrimaryKeyRelatedField(
        queryset=Lesson.objects.filter(deleted_at__isnull=True)
    )
    
    class Meta:
        model = LessonGallery
        fields = ['lesson', 'image']
        
    def validate(self, data):
        # Call parent's validate method first
        data = super().validate(data)
        
        try:
            gallery = LessonGallery.objects.get(
                lesson=data['lesson']
            )
            
            if gallery and gallery.images_count >= 5:
                raise serializers.ValidationError("This lesson already has maximum number of images (5)")
            
            data['gallery'] = gallery
        except LessonGallery.DoesNotExist:
            data['gallery'] = None
            
        return data
        
    def create(self, validated_data):
        image = validated_data.pop('image')
        gallery = validated_data.pop('gallery')
        
        try:
            image_url = upload_image_to_firebase(image)
            
            if gallery:
                gallery.image_urls.append(image_url)
                gallery.save()
                return gallery
            else:
                return LessonGallery.objects.create(
                    lesson=validated_data['lesson'],
                    image_urls=[image_url]
                )
        except Exception as e:
            raise serializers.ValidationError({'image': str(e)}) 