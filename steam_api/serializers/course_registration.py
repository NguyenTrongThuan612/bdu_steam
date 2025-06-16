from rest_framework import serializers
from steam_api.models.course_registration import CourseRegistration
from steam_api.serializers.student import StudentSerializer
from steam_api.serializers.class_room import ClassRoomSerializer

class CourseRegistrationSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    class_room = ClassRoomSerializer(read_only=True)
    
    class Meta:
        model = CourseRegistration
        fields = [
            'id', 'student', 'class_room', 'status', 
            'amount', 'paid_amount', 'payment_method', 'payment_status',
            'note', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class CreateCourseRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseRegistration
        fields = ['student', 'class_room', 'note']
        
    def validate(self, data):
        # Kiểm tra xem học viên đã đăng ký lớp này chưa
        try:
            existing_registration = CourseRegistration.objects.get(
                student=data['student'],
                class_room=data['class_room'],
                deleted_at__isnull=True
            )
            if existing_registration.status not in ['rejected', 'cancelled']:
                raise serializers.ValidationError("Student has already registered for this class")
        except CourseRegistration.DoesNotExist:
            pass
            
        # Kiểm tra số lượng học viên trong lớp
        class_room = data['class_room']
        if class_room.students.count() >= class_room.max_students:
            raise serializers.ValidationError("Class is full")
            
        # Lấy học phí từ khóa học
        data['amount'] = class_room.course.price
            
        return data

class UpdateCourseRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseRegistration
        fields = ['status', 'paid_amount', 'payment_method', 'note']
        extra_kwargs = {
            'status': {'required': False},
            'paid_amount': {'required': False},
            'payment_method': {'required': False},
            'note': {'required': False}
        }
        
    def validate_status(self, value):
        # Kiểm tra các điều kiện khi thay đổi trạng thái
        if self.instance:
            if self.instance.status == 'approved' and value != 'cancelled':
                raise serializers.ValidationError("Cannot change status of approved registration except to cancelled")
            if self.instance.status in ['rejected', 'cancelled'] and value != self.instance.status:
                raise serializers.ValidationError("Cannot change status of rejected or cancelled registration")
        return value
        
    def validate(self, data):
        if 'paid_amount' in data:
            # Kiểm tra số tiền thanh toán không vượt quá học phí
            if data['paid_amount'] > self.instance.amount:
                raise serializers.ValidationError({'paid_amount': 'Paid amount cannot exceed total amount'})
        return data 