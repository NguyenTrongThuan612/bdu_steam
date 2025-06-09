from rest_framework import serializers
from steam_api.models.lesson_evaluation import LessonEvaluation
from steam_api.serializers.student import StudentSerializer

class LessonEvaluationSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    class_room_name = serializers.CharField(source='module.class_room.name', read_only=True)
    module_name = serializers.CharField(source='module.name', read_only=True)
    
    class Meta:
        model = LessonEvaluation
        fields = [
            'id', 'module', 'lesson_number', 'student', 'class_room_name', 'module_name',
            'focus_score', 'punctuality_score', 'interaction_score', 'project_idea_score',
            'critical_thinking_score', 'teamwork_score', 'idea_sharing_score',
            'creativity_score', 'communication_score', 'homework_score',
            'old_knowledge_score', 'new_knowledge_score', 'comment',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class CreateLessonEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonEvaluation
        fields = [
            'module', 'lesson_number', 'student',
            'focus_score', 'punctuality_score', 'interaction_score', 'project_idea_score',
            'critical_thinking_score', 'teamwork_score', 'idea_sharing_score',
            'creativity_score', 'communication_score', 'homework_score',
            'old_knowledge_score', 'new_knowledge_score', 'comment'
        ]
        
    def validate(self, data):
        # Kiểm tra xem học viên có thuộc lớp học không
        if data['student'] not in data['module'].class_room.students.all():
            raise serializers.ValidationError("Student is not enrolled in this class")
            
        # Kiểm tra số buổi học có hợp lệ không
        if data['lesson_number'] > data['module'].total_lessons:
            raise serializers.ValidationError(
                f"Lesson number must not exceed total lessons of module ({data['module'].total_lessons})"
            )
            
        # Kiểm tra xem đã có đánh giá cho học viên này chưa
        try:
            existing_evaluation = LessonEvaluation.objects.get(
                module=data['module'],
                lesson_number=data['lesson_number'],
                student=data['student'],
                deleted_at__isnull=True
            )
            raise serializers.ValidationError("Evaluation for this student already exists")
        except LessonEvaluation.DoesNotExist:
            pass
            
        return data

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