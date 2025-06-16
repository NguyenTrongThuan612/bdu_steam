from django.db import models
from django.utils import timezone
from steam_api.models.student import Student
from steam_api.models.class_room import ClassRoom

class CourseRegistration(models.Model):
    class Meta:
        db_table = "course_registrations"
        unique_together = ('student', 'class_room')
        
    id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='registrations')
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='registrations')
    
    # Trạng thái đăng ký
    STATUS_CHOICES = [
        ('pending', 'Pending'),  # Chờ xác nhận
        ('approved', 'Approved'),  # Đã xác nhận
        ('rejected', 'Rejected'),  # Từ chối
        ('cancelled', 'Cancelled'),  # Hủy đăng ký
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Thông tin thanh toán
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Số tiền phải thanh toán
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Số tiền đã thanh toán
    payment_method = models.CharField(max_length=50, null=True, blank=True)  # Phương thức thanh toán
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('unpaid', 'Unpaid'),  # Chưa thanh toán
            ('partially_paid', 'Partially Paid'),  # Thanh toán một phần
            ('fully_paid', 'Fully Paid'),  # Đã thanh toán đủ
        ],
        default='unpaid'
    )
    
    # Ghi chú
    note = models.TextField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.student.first_name} - {self.class_room.name} ({self.status})"
        
    def save(self, *args, **kwargs):
        # Cập nhật payment_status dựa trên số tiền đã thanh toán
        if self.paid_amount >= self.amount:
            self.payment_status = 'fully_paid'
        elif self.paid_amount > 0:
            self.payment_status = 'partially_paid'
        else:
            self.payment_status = 'unpaid'
            
        # Khi registration được approved và thanh toán đủ, thêm học viên vào lớp
        if self.status == 'approved' and self.payment_status == 'fully_paid':
            self.class_room.students.add(self.student)
            
        super().save(*args, **kwargs) 