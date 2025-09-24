import logging
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from steam_api.helpers.response import RestResponse
from steam_api.models.course import Course
from steam_api.models.student import Student
from steam_api.models.student_registration import StudentRegistration, StudentRegistrationStatus
from steam_api.serializers.course import CourseSerializer
from steam_api.middlewares.app_authentication import AppAuthentication  

class AppCourseView(viewsets.ViewSet):
    authentication_classes = (AppAuthentication,)
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'student',
                openapi.IN_QUERY,
                description='Filter by student ID',
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: CourseSerializer(many=True),
            500: openapi.Response(
                description='Internal Server Error',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def list(self, request):
        try:
            logging.getLogger().info("AppCourseView.list")
            student_id = request.query_params.get('student', None)
            courses = Course.objects.filter(deleted_at__isnull=True, is_active=True)

            if student_id:
                try:
                    registration = StudentRegistration.objects.filter(
                        app_user=request.user,
                        status=StudentRegistrationStatus.APPROVED,
                        student__id=student_id,
                        deleted_at__isnull=True
                    ).first()
                    
                    if not registration:
                        return RestResponse(message="Bạn không có quyền xem khóa học của học viên này!", status=status.HTTP_403_FORBIDDEN).response
                    
                    if not StudentRegistration.objects.filter(
                        app_user=request.user,
                        status=StudentRegistrationStatus.APPROVED,
                        student=registration.student,
                        deleted_at__isnull=True
                    ).exists():
                        return RestResponse(message="Bạn không có quyền xem khóa học của học viên này!", status=status.HTTP_403_FORBIDDEN).response
                    
                    courses = courses.filter(classes__in=registration.class_room).distinct()
                except Student.DoesNotExist:
                    return RestResponse(message="Student not found!", status=status.HTTP_404_NOT_FOUND).response

            serializer = CourseSerializer(courses, many=True, context={'request': request})
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("AppCourseView.list exc=%s, params=%s", e, request.query_params)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response 