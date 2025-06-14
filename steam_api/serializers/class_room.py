from rest_framework import serializers
from steam_api.models.class_room import ClassRoom
from steam_api.helpers.firebase_storage import upload_image_to_firebase
from steam_api.serializers.web_user import WebUserSerializer
from steam_api.models.web_user import WebUserRole

class ClassRoomSerializer(serializers.ModelSerializer):
    teacher = WebUserSerializer(read_only=True)
    teaching_assistant = WebUserSerializer(read_only=True)
    
    class Meta:
        model = ClassRoom
        fields = ['id', 'name', 'description', 'thumbnail_url', 'course', 'teacher', 'teaching_assistant',
                 'max_students', 'start_date', 'end_date', 'schedule', 'total_sessions', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class CreateClassRoomSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(write_only=True, required=False)
    
    class Meta:
        model = ClassRoom
        fields = ['name', 'description', 'thumbnail', 'course', 'teacher', 'teaching_assistant', 'max_students',
                 'start_date', 'end_date', 'schedule', 'total_sessions']

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date must be after start date")
            
        if 'teacher' in data and 'teaching_assistant' in data and data['teacher'] == data['teaching_assistant']:
            raise serializers.ValidationError("Teacher and teaching assistant cannot be the same person")
            
        if 'teacher' in data and data['teacher'].role != WebUserRole.TEACHER:
            raise serializers.ValidationError("Assigned teacher must have teacher role")
            
        if 'teaching_assistant' in data and data['teaching_assistant'].role != WebUserRole.TEACHER:
            raise serializers.ValidationError("Teaching assistant must have teacher role")

        if 'total_sessions' in data and data['total_sessions'] < 0:
            raise serializers.ValidationError("Total sessions cannot be negative")
            
        return data

    def create(self, validated_data):
        thumbnail = validated_data.pop('thumbnail', None)
        
        if thumbnail:
            try:
                thumbnail_url = upload_image_to_firebase(thumbnail)
                validated_data['thumbnail_url'] = thumbnail_url
            except Exception as e:
                raise serializers.ValidationError({'thumbnail': str(e)})
                
        return super().create(validated_data)

class UpdateClassRoomSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(write_only=True, required=False)
    
    class Meta:
        model = ClassRoom
        fields = ['name', 'description', 'thumbnail', 'teacher', 'teaching_assistant',
                 'max_students', 'start_date', 'end_date', 'schedule', 'total_sessions', 'is_active']
        extra_kwargs = {
            'name': {'required': False},
            'description': {'required': False},
            'teacher': {'required': False},
            'teaching_assistant': {'required': False},
            'max_students': {'required': False},
            'start_date': {'required': False},
            'end_date': {'required': False},
            'schedule': {'required': False},
            'total_sessions': {'required': False},
            'is_active': {'required': False}
        }

    def validate(self, data):
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError("End date must be after start date")
        elif 'start_date' in data and self.instance:
            if data['start_date'] > self.instance.end_date:
                raise serializers.ValidationError("End date must be after start date")
        elif 'end_date' in data and self.instance:
            if self.instance.start_date > data['end_date']:
                raise serializers.ValidationError("End date must be after start date")
                
        teacher = data.get('teacher', self.instance.teacher if self.instance else None)
        assistant = data.get('teaching_assistant', self.instance.teaching_assistant if self.instance else None)
        if teacher and assistant and teacher == assistant:
            raise serializers.ValidationError("Teacher and teaching assistant cannot be the same person")
            
        if teacher and teacher.role != WebUserRole.TEACHER:
            raise serializers.ValidationError("Assigned teacher must have teacher role")
            
        if assistant and assistant.role != WebUserRole.TEACHER:
            raise serializers.ValidationError("Teaching assistant must have teacher role")

        if 'total_sessions' in data and data['total_sessions'] < 0:
            raise serializers.ValidationError("Total sessions cannot be negative")
            
        return data

    def update(self, instance, validated_data):
        thumbnail = validated_data.pop('thumbnail', None)
        
        if thumbnail:
            try:
                thumbnail_url = upload_image_to_firebase(thumbnail)
                validated_data['thumbnail_url'] = thumbnail_url
            except Exception as e:
                raise serializers.ValidationError({'thumbnail': str(e)})
                
        return super().update(instance, validated_data)

class ListClassRoomSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    assistant_name = serializers.CharField(source='teaching_assistant.full_name', read_only=True)
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ClassRoom
        fields = ['id', 'name', 'total_sessions', 'start_date', 'teacher_name', 'assistant_name', 'student_count']
        
    def get_student_count(self, obj):
        return obj.students.count() if hasattr(obj, 'students') else 0 