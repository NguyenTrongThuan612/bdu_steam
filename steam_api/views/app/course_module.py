import logging
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.app_authentication import AppAuthentication
from steam_api.models.student_registration import StudentRegistration, StudentRegistrationStatus
from steam_api.models.course_registration import CourseRegistration
from steam_api.models.course_module import CourseModule
from steam_api.serializers.course_module import CourseModuleSerializer

class AppCourseModuleView(viewsets.ViewSet):
    authentication_classes = (AppAuthentication,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'student',
                openapi.IN_QUERY,
                description='Filter by student ID',
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'class_room',
                openapi.IN_QUERY,
                description='Filter by class room ID',
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: CourseModuleSerializer(many=True),
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
            logging.getLogger().info("AppCourseModuleView.list user=%s, params=%s", request.user.id, request.query_params)
            
            student_id = request.query_params.get('student', None)
            class_room_id = request.query_params.get('class_room', None)
            
            student_ids = StudentRegistration.objects.filter(
                app_user=request.user,
                status=StudentRegistrationStatus.APPROVED,
                deleted_at__isnull=True
            )
            
            if student_id:
                student_ids = student_ids.filter(student_id=student_id)
                
            student_ids = student_ids.values_list('student_id', flat=True)

            class_rooms = CourseRegistration.objects.filter(
                student_id__in=student_ids,
                status='approved',
                deleted_at__isnull=True
            ).values_list('class_room_id', flat=True).distinct()
            
            modules = CourseModule.objects.filter(
                deleted_at__isnull=True
            )
            
            if class_room_id:
                modules = modules.filter(class_room_id=class_room_id)
            else:
                modules = modules.filter(class_room_id__in=class_rooms)
                
            modules = modules.select_related(
                'class_room',
                'class_room__course'
            ).order_by('class_room__name', 'sequence_number')

            serializer = CourseModuleSerializer(modules, many=True)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("AppCourseModuleView.list exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response 