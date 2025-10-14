from rest_framework import serializers
from steam_api.models.lesson_documentation import LessonDocumentation
from steam_api.models.lesson import Lesson

class LessonDocumentationSerializer(serializers.ModelSerializer):
    link = serializers.SerializerMethodField()

    def get_link(self, obj):
        return obj.get_link()

    class Meta:
        model = LessonDocumentation
        fields = '__all__'

class CreateLessonDocumentationSerializer(serializers.ModelSerializer):
    link = serializers.URLField(required=True)
    lesson = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.filter(deleted_at__isnull=True))

    class Meta:
        model = LessonDocumentation
        fields = ['lesson', 'link']

    def create(self, validated_data):
        lesson = validated_data['lesson']
        link = validated_data['link']
        return LessonDocumentation.objects.create(lesson=lesson, link=link)

class UpdateLessonDocumentationSerializer(serializers.ModelSerializer):
    link = serializers.URLField(required=True)
    
    class Meta:
        model = LessonDocumentation
        fields = ['link']

    def update(self, instance, validated_data):
        instance.link = validated_data['link']
        instance.save()
        return instance