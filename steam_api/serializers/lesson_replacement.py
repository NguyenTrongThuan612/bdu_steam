from rest_framework import serializers
from steam_api.models.lesson_replacement import LessonReplacement

class LessonReplacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonReplacement
        fields = "__all__"
        
class CreateLessonReplacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonReplacement
        fields = ['schedule']