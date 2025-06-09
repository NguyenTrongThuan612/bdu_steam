from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from steam_api.models.course_module import CourseModule
from steam_api.models.student import Student

class LessonEvaluation(models.Model):
    class Meta:
        db_table = "lesson_evaluations"
        unique_together = ('module', 'lesson_number', 'student')
        ordering = ['module__sequence_number', 'lesson_number']
        
    id = models.BigAutoField(primary_key=True)
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='lesson_evaluations')
    lesson_number = models.IntegerField(
        validators=[MinValueValidator(1)], 
        help_text="The sequence number of the lesson in this module"
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='lesson_evaluations')
    
    # Mức độ tập trung (1-5)
    focus_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1: Không tập trung, 2: Ít tập trung, 3: Tập trung khá, 4: Tập trung tốt, 5: Hoàn toàn tập trung"
    )
    
    # Đi muộn/Trễ (1-5)
    punctuality_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1: Thường xuyên đi muộn/về sớm, 2: Hay đi muộn/về sớm, 3: Thỉnh thoảng đi muộn/về sớm, 4: Hiếm khi đi muộn/về sớm, 5: Luôn đúng giờ"
    )
    
    # Mức độ tương tác (1-5)
    interaction_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1: Thụ động, 2: Ít tương tác, 3: Tương tác trung bình, 4: Tương tác tốt, 5: Tương tác xuất sắc"
    )
    
    # Ý tưởng dự án (1-5)
    project_idea_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1: Không có ý tưởng, 2: Ý tưởng kém chất lượng, 3: Ý tưởng trung bình, 4: Ý tưởng tốt, 5: Ý tưởng xuất sắc"
    )
    
    # Tư duy phản biện (1-5)
    critical_thinking_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1: Không có tư duy phản biện, 2: Tư duy phản biện yếu, 3: Tư duy phản biện trung bình, 4: Tư duy phản biện tốt, 5: Tư duy phản biện xuất sắc"
    )
    
    # Hợp tác nhóm (1-5)
    teamwork_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1: Không hợp tác, 2: Ít hợp tác, 3: Hợp tác trung bình, 4: Hợp tác tốt, 5: Hợp tác xuất sắc"
    )
    
    # Chia sẻ ý tưởng (1-5)
    idea_sharing_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1: Không chia sẻ, 2: Ít chia sẻ, 3: Chia sẻ trung bình, 4: Chia sẻ tốt, 5: Chia sẻ xuất sắc"
    )
    
    # Sáng tạo (1-5)
    creativity_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1: Không sáng tạo, 2: Ít sáng tạo, 3: Sáng tạo trung bình, 4: Sáng tạo tốt, 5: Sáng tạo xuất sắc"
    )
    
    # Giao tiếp (1-5)
    communication_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1: Kém hiệu quả, 2: Chưa hiệu quả, 3: Trung bình, 4: Tốt, 5: Xuất sắc"
    )
    
    # Bài tập về nhà (1-5)
    homework_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1: Không hoàn thành, 2: Hoàn thành kém chất lượng, 3: Hoàn thành trung bình, 4: Hoàn thành tốt, 5: Hoàn thành xuất sắc"
    )
    
    # Kiến thức cũ (1-5)
    old_knowledge_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1: Không nắm vững, 2: Nắm vững yếu, 3: Nắm vững trung bình, 4: Nắm vững tốt, 5: Nắm vững xuất sắc"
    )
    
    # Kiến thức mới (1-5)
    new_knowledge_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1: Khó tiếp thu, 2: Tiếp thu chậm, 3: Tiếp thu trung bình, 4: Tiếp thu tốt, 5: Tiếp thu xuất sắc"
    )
    
    comment = models.TextField(
        null=True, 
        blank=True,
        help_text="Nhận xét thêm của giáo viên"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.module.class_room.name} - {self.module.name} - Lesson {self.lesson_number} - {self.student.first_name}"