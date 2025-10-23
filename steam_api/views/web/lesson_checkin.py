from datetime import datetime
from zoneinfo import ZoneInfo

import logging
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.permissions import IsNotRoot, IsTeacher
from steam_api.middlewares.web_authentication import WebUserAuthentication
from steam_api.models.lesson import Lesson
from steam_api.models.lesson_checkin import LessonCheckin
from steam_api.models.web_user import WebUserRole
from steam_api.serializers.lesson_checkin import LessonCheckinSerializer, LessonCheckinCreateSerializer

class WebLessonCheckinView(viewsets.ViewSet):
    authentication_classes = (WebUserAuthentication,)

    def get_permissions(self):
        if self.action == 'create':
            return [IsTeacher()]
        return [IsNotRoot()]

    @swagger_auto_schema(
        request_body=LessonCheckinCreateSerializer(),
        responses={
            200: LessonCheckinSerializer(),
            400: 'Bad Request',
            403: 'Forbidden',
            404: 'Not Found',
            500: 'Internal Server Error'
        }
    )
    def create(self, request):
        try:
            logging.getLogger().info(
                "WebLessonCheckinView.create user=%s, req=%s",
                request.user.id, request.data
            )

            checkin_time = datetime.now(ZoneInfo('Asia/Ho_Chi_Minh'))
            logging.getLogger().info(f"WebLessonCheckinView.create checkin_time: {checkin_time}")

            serializer = LessonCheckinCreateSerializer(
                data=request.data,
                context={'user': request.user, 'checkin_time': checkin_time}
            )
            
            if not serializer.is_valid():
                return RestResponse(
                    message="Dữ liệu không hợp lệ!",
                    status=status.HTTP_400_BAD_REQUEST
                ).response
            
            lesson : Lesson = serializer.validated_data['lesson']

            if not lesson.module.class_room.teacher_id == request.user.id and not lesson.module.class_room.teaching_assistant_id == request.user.id:
                return RestResponse(
                    message="Bạn không có quyền checkin buổi học này!",
                    status=status.HTTP_403_FORBIDDEN
                ).response
            
            if LessonCheckin.objects.filter(lesson=lesson, user=request.user, deleted_at__isnull=True).exists():
                return RestResponse(
                    message="Bạn đã checkin buổi học này rồi!",
                    status=status.HTTP_400_BAD_REQUEST
                ).response
            
            if not lesson.module.class_room.schedule:
                return RestResponse(
                    message="Lớp học không có lịch học!",
                    status=status.HTTP_400_BAD_REQUEST
                ).response

            logging.getLogger().info(f"WebLessonCheckinView.create lesson.start_datetime: {lesson.start_datetime}")
            time_diff = abs((lesson.start_datetime - checkin_time).total_seconds())
            logging.getLogger().info(f"WebLessonCheckinView.create time_diff: {time_diff}")

            if time_diff > 900:
                return RestResponse(
                    message="Checkin chỉ được thực hiện trong vòng 15 phút trước hoặc sau buổi học!",
                    status=status.HTTP_400_BAD_REQUEST
                ).response
            
            checkin = serializer.save()
                
            return RestResponse(
                data=LessonCheckinSerializer(checkin).data,
                status=status.HTTP_200_OK
            ).response
            
        except Exception as e:
            logging.getLogger().exception("WebLessonCheckinView.checkin exc=%s", e)
            return RestResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ).response
            
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'lesson',
                openapi.IN_QUERY,
                description='Filter by lesson ID',
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
                'class_room',
                openapi.IN_QUERY,
                description='Filter by class room ID',
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'teacher',
                openapi.IN_QUERY,
                description='Filter by teacher ID',
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: LessonCheckinSerializer(many=True),
            500: 'Internal Server Error'
        }
    )
    def list(self, request):
        try:
            logging.getLogger().info(
                "WebLessonCheckinView.list user=%s, params=%s",
                request.user.id, request.query_params
            )
            
            lesson_id = request.query_params.get('lesson')
            module_id = request.query_params.get('module')
            class_room_id = request.query_params.get('class_room')
            teacher_id = request.query_params.get('teacher')

            queryset = LessonCheckin.objects.filter(deleted_at__isnull=True)
            
            if lesson_id:
                queryset = queryset.filter(lesson_id=lesson_id)
                
            if module_id:
                queryset = queryset.filter(lesson__module_id=module_id)
                
            if class_room_id:
                queryset = queryset.filter(lesson__module__class_room_id=class_room_id)

            if teacher_id:
                queryset = queryset.filter(
                    lesson__module__class_room__teacher_id=teacher_id
                ) | queryset.filter(
                    lesson__module__class_room__teaching_assistant_id=teacher_id
                )
                
            if request.user.role == WebUserRole.TEACHER:
                queryset = queryset.filter(
                    lesson__module__class_room__teacher_id=request.user.id
                ) | queryset.filter(
                    lesson__module__class_room__teaching_assistant_id=request.user.id
                )
            
            queryset = queryset.select_related(
                'lesson',
                'lesson__module',
                'lesson__module__class_room',
                'user'
            ).order_by('-created_at')
            
            serializer = LessonCheckinSerializer(queryset, many=True)
            return RestResponse(
                data=serializer.data,
                status=status.HTTP_200_OK
            ).response
            
        except Exception as e:
            logging.getLogger().exception("WebLessonCheckinView.list exc=%s", e)
            return RestResponse(
                data={"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ).response 