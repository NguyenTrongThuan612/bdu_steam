import logging
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q

from steam_api.helpers.response import RestResponse
from steam_api.models.attendance import Attendance
from steam_api.models.web_user import WebUserRole
from steam_api.serializers.attendance import AttendanceSerializer, CreateAttendanceSerializer
from steam_api.middlewares.permissions import IsNotRoot, IsTeacher
from steam_api.middlewares.web_authentication import WebUserAuthentication

class WebAttendanceView(viewsets.ViewSet):
    authentication_classes = (WebUserAuthentication,)

    def get_permissions(self):
        if self.action in ['create']:
            return [IsTeacher()]
        return [IsNotRoot()]

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
                'classroom',
                openapi.IN_QUERY,
                description='Filter by classroom ID',
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'module',
                openapi.IN_QUERY,
                description='Filter by module ID',
                type=openapi.TYPE_INTEGER,
                required=False
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
            logging.getLogger().info("WebAttendanceView.list params=%s", request.query_params)
            
            student_id = request.query_params.get('student')
            classroom_id = request.query_params.get('classroom')
            module_id = request.query_params.get('module')
            
            attendances = Attendance.objects.filter(deleted_at__isnull=True)
            
            if request.user.role == WebUserRole.TEACHER:
                attendances = attendances.filter(
                    Q(lesson__module__class_room__teacher=request.user) |
                    Q(lesson__module__class_room__teaching_assistant=request.user)
                )

            if student_id:
                attendances = attendances.filter(student_id=student_id)
                
            if classroom_id:
                attendances = attendances.filter(lesson__module__class_room_id=classroom_id)
                
            if module_id:
                attendances = attendances.filter(lesson__module_id=module_id)
                
            attendances = attendances.select_related('student', 'lesson').order_by('-check_in_time')
                
            serializer = AttendanceSerializer(attendances, many=True)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebAttendanceView.list exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=CreateAttendanceSerializer,
        responses={
            201: AttendanceSerializer,
            400: openapi.Response(
                description='Bad Request',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
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
    def create(self, request):
        try:
            logging.getLogger().info("WebAttendanceView.create req=%s", request.data)
            
            serializer = CreateAttendanceSerializer(data=request.data, context={'request': request})
            if not serializer.is_valid():
                return RestResponse(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST).response
                
            attendance = serializer.save()
            return RestResponse(data=AttendanceSerializer(attendance).data, status=status.HTTP_201_CREATED).response
        except Exception as e:
            logging.getLogger().exception("WebAttendanceView.create exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response 