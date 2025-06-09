from rest_framework import serializers
from steam_api.models.lesson_gallery import LessonGallery
from steam_api.helpers.firebase_storage import upload_image_to_firebase

class LessonGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonGallery
        fields = ['id', 'module', 'lesson_number', 'image_urls', 'created_at']
        read_only_fields = ['id', 'created_at']

class CreateLessonGallerySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True)
    
    class Meta:
        model = LessonGallery
        fields = ['module', 'lesson_number', 'image']
        
    def validate(self, data):
        if data['lesson_number'] > data['module'].total_lessons:
            raise serializers.ValidationError(
                f"Lesson number cannot be greater than total lessons in this module ({data['module'].total_lessons})"
            )
            
        try:
            gallery = LessonGallery.objects.get(
                module=data['module'],
                lesson_number=data['lesson_number']
            )
        except LessonGallery.DoesNotExist:
            gallery = None
            
        if gallery and gallery.images_count >= 5:
            raise serializers.ValidationError("This lesson already has maximum number of images (5)")
            
        data['gallery'] = gallery
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
                    module=validated_data['module'],
                    lesson_number=validated_data['lesson_number'],
                    image_urls=[image_url]
                )
        except Exception as e:
            raise serializers.ValidationError({'image': str(e)}) 