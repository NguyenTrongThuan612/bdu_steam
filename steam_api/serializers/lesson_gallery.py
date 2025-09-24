from rest_framework import serializers
from steam_api.models.lesson_gallery import LessonGallery
from steam_api.helpers.local_storage import upload_file_to_local
from steam_api.models.lesson import Lesson

class LessonGallerySerializer(serializers.ModelSerializer):
    image_urls = serializers.SerializerMethodField()

    def get_image_urls(self, obj):
        return [self.context.get('request').build_absolute_uri(image_url) for image_url in obj.image_urls]

    class Meta:
        model = LessonGallery
        fields = "__all__"

class CreateLessonGallerySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True)
    lesson = serializers.PrimaryKeyRelatedField(
        queryset=Lesson.objects.filter(deleted_at__isnull=True)
    )
    
    class Meta:
        model = LessonGallery
        fields = ['lesson', 'image']
        
    def create(self, validated_data):
        image = validated_data.pop('image')
        lesson = validated_data.pop('lesson')
        
        try:
            image_url = upload_file_to_local(image)
            
            if LessonGallery.objects.filter(
                lesson=lesson,
                deleted_at__isnull=True
            ).exists():
                gallery = LessonGallery.objects.get(
                    lesson=lesson,
                    deleted_at__isnull=True
                )
                gallery.image_urls.append(image_url)
                gallery.save()
                return gallery
            
            return LessonGallery.objects.create(
                lesson=lesson,
                image_urls=[image_url]
            )
        except Exception as e:
            raise serializers.ValidationError({'image': str(e)}) 