import logging
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.app_authentication import AppAuthentication
from steam_api.models.student_registration import StudentRegistration, StudentRegistrationStatus
from steam_api.models.course_registration import CourseRegistration
from steam_api.models.attendance import Attendance
from steam_api.serializers.attendance import AttendanceSerializer

class AppAttendanceView(viewsets.ViewSet):
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
            ),
            openapi.Parameter(
                'module',
                openapi.IN_QUERY,
                description='Filter by module ID',
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'lesson',
                openapi.IN_QUERY,
                description='Filter by lesson ID',
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description='Filter by attendance status (present/absent/late/excused)',
                type=openapi.TYPE_STRING,
                required=False,
                enum=['present', 'absent', 'late', 'excused']
            )
        ],
        responses={
            200: AttendanceSerializer(many=True),
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
            logging.getLogger().info("AppAttendanceView.list user=%s, params=%s", request.user.id, request.query_params)
            
            student_id = request.query_params.get('student', None)
            class_room_id = request.query_params.get('class_room', None)
            module_id = request.query_params.get('module', None)
            lesson_id = request.query_params.get('lesson', None)
            status_filter = request.query_params.get('status', None)
            
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
            
            attendances = Attendance.objects.filter(
                student_id__in=student_ids,
                deleted_at__isnull=True
            )
            
            if lesson_id:
                attendances = attendances.filter(lesson_id=lesson_id)
            elif module_id:
                attendances = attendances.filter(lesson__module_id=module_id)
            elif class_room_id:
                attendances = attendances.filter(lesson__module__class_room_id=class_room_id)
            else:
                attendances = attendances.filter(lesson__module__class_room_id__in=class_rooms)
                
            if status_filter:
                attendances = attendances.filter(status=status_filter)
                
            attendances = attendances.select_related(
                'student',
                'lesson',
                'lesson__module',
                'lesson__module__class_room',
                'lesson__module__class_room__course'
            ).order_by(
                '-check_in_time',
                'lesson__module__class_room__name',
                'lesson__module__sequence_number',
                'lesson__sequence_number'
            )

            serializer = AttendanceSerializer(attendances, many=True)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("AppAttendanceView.list exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response 