from rest_framework import serializers
from steam_api.models.lesson_evaluation import LessonEvaluation
from steam_api.serializers.student import StudentSerializer
from steam_api.models.student import Student
from steam_api.models.lesson import Lesson
from steam_api.serializers.lesson import LessonSerializer

class LessonEvaluationSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    lesson = LessonSerializer(read_only=True)
    class_room_name = serializers.CharField(source='lesson.module.class_room.name', read_only=True)
    module_name = serializers.CharField(source='lesson.module.name', read_only=True)
    
    class Meta:
        model = LessonEvaluation
        fields = "__all__"

class CreateLessonEvaluationSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.filter(is_active=True, deleted_at__isnull=True)
    )
    lesson = serializers.PrimaryKeyRelatedField(
        queryset=Lesson.objects.filter(deleted_at__isnull=True)
    )
    
    class Meta:
        model = LessonEvaluation
        fields = [
            'lesson', 'student',
            'focus_score', 'punctuality_score', 'interaction_score', 'project_idea_score',
            'critical_thinking_score', 'teamwork_score', 'idea_sharing_score',
            'creativity_score', 'communication_score', 'homework_score',
            'old_knowledge_score', 'new_knowledge_score', 'comment'
        ]

class UpdateLessonEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonEvaluation
        fields = [
            'focus_score', 'punctuality_score', 'interaction_score', 'project_idea_score',
            'critical_thinking_score', 'teamwork_score', 'idea_sharing_score',
            'creativity_score', 'communication_score', 'homework_score',
            'old_knowledge_score', 'new_knowledge_score', 'comment'
        ]
        extra_kwargs = {
            'focus_score': {'required': False},
            'punctuality_score': {'required': False},
            'interaction_score': {'required': False},
            'project_idea_score': {'required': False},
            'critical_thinking_score': {'required': False},
            'teamwork_score': {'required': False},
            'idea_sharing_score': {'required': False},
            'creativity_score': {'required': False},
            'communication_score': {'required': False},
            'homework_score': {'required': False},
            'old_knowledge_score': {'required': False},
            'new_knowledge_score': {'required': False},
            'comment': {'required': False}
        } 