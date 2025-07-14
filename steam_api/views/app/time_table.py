import logging
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.app_authentication import AppAuthentication
from steam_api.models.class_room import ClassRoom
from steam_api.models.lesson import Lesson
from steam_api.models.student import Student
from steam_api.models.student_registration import StudentRegistration, StudentRegistrationStatus
from steam_api.models.course_registration import CourseRegistration
from steam_api.serializers.lesson import LessonSerializer

class AppTimeTableView(viewsets.ViewSet):
    authentication_classes = (AppAuthentication,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'student',
                openapi.IN_QUERY,
                description='Filter by student ID',
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'class_room',
                openapi.IN_QUERY,
                description='Filter by class room ID',
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ]
    )   
    def list(self, request):
        try:
            student_id = request.query_params.get('student', None)
            class_room_id = request.query_params.get('class_room', None)

            if not student_id or not class_room_id:
                return RestResponse(message="Student and class room are required!", status=status.HTTP_400_BAD_REQUEST).response
            
            student = Student.objects.get(id=student_id)
            class_room = ClassRoom.objects.get(id=class_room_id)

            if not StudentRegistration.objects.filter(student=student, status="approved", deleted_at__isnull=True).exists():
                return RestResponse(message="Bạn không có quyền xem lịch học của học viên này!", status=status.HTTP_403_FORBIDDEN).response

            if not CourseRegistration.objects.filter(student=student, class_room=class_room, status="approved", deleted_at__isnull=True).exists():
                return RestResponse(message="Học viên này không đăng ký khóa học này!", status=status.HTTP_403_FORBIDDEN).response
            
            lessons = Lesson.objects.filter(module__class_room=class_room).order_by("module__sequence_number", "sequence_number")
            
            return RestResponse(data=LessonSerializer(lessons, many=True).data, status=status.HTTP_200_OK).response

        except Student.DoesNotExist:
            return RestResponse(message="Student not found!", status=status.HTTP_404_NOT_FOUND).response
        except ClassRoom.DoesNotExist:
            return RestResponse(message="Class room not found!", status=status.HTTP_404_NOT_FOUND).response
        except Exception as e:
            logging.getLogger().exception("AppTimeTableView.list exc=%s, params=%s", e, request.query_params)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR).response