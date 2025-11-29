import logging
from zoneinfo import ZoneInfo
from rest_framework import viewsets, status
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from datetime import datetime, timedelta

from steam_api.helpers.response import RestResponse
from steam_api.models.lesson import Lesson
from steam_api.models.lesson_replacement import LessonReplacement
from steam_api.models.web_user import WebUserRole
from steam_api.serializers.lesson import LessonSerializer, UpdateLessonSerializer, CreateLessonSerializer
from steam_api.middlewares.permissions import IsManager, IsNotRoot
from steam_api.middlewares.web_authentication import WebUserAuthentication
from steam_api.serializers.lesson_replacement import CreateLessonReplacementSerializer, LessonReplacementSerializer

class WebLessonView(viewsets.ViewSet):
    authentication_classes = (WebUserAuthentication,)

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsManager()]
        return [IsNotRoot()]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'module',
                openapi.IN_QUERY,
                description='Filter lessons by module ID',
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description='Filter lessons by status (not_started, in_progress, completed)',
                type=openapi.TYPE_STRING,
                required=False,
                enum=['not_started', 'in_progress', 'completed']
            ),
            openapi.Parameter(
                'teacher',
                openapi.IN_QUERY,
                description='Filter lessons by teacher or teaching assistant ID',
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'lesson_date',
                openapi.IN_QUERY,
                description='Filter lessons by date (format: YYYY-MM-DD)',
                type=openapi.TYPE_STRING,
                required=False
            )
        ],
        responses={
            200: LessonSerializer(many=True),
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
            logging.getLogger().info("WebLessonView.list params=%s", request.query_params)
            module_id = request.query_params.get('module')
            status_filter = request.query_params.get('status')
            teacher_id = request.query_params.get('teacher')
            date_str = request.query_params.get('lesson_date')
            lessons = Lesson.objects.filter(deleted_at__isnull=True)

            # if request.user.role == WebUserRole.TEACHER:
            #     lessons = lessons.filter(
            #         Q(module__class_room__teacher=request.user) |
            #         Q(module__class_room__teaching_assistant=request.user)
            #     )
            
            if module_id:
                lessons = lessons.filter(module_id=module_id)

            if teacher_id:
                lessons = lessons.filter(
                    Q(module__class_room__teacher_id=teacher_id) |
                    Q(module__class_room__teaching_assistant_id=teacher_id)
                )
                
            lessons = lessons.order_by('module__sequence_number', 'sequence_number')
            
            if date_str:
                try:
                    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    filtered_lessons = []
                    for lesson in lessons:
                        if lesson.start_datetime and lesson.start_datetime.date() == target_date:
                            filtered_lessons.append(lesson)
                    lessons = filtered_lessons
                except ValueError:
                    return RestResponse(
                        data={"error": "Invalid date format. Use YYYY-MM-DD"},
                        status=status.HTTP_400_BAD_REQUEST
                    ).response
            
            if status_filter:
                filtered_lessons = []
                for lesson in lessons:
                    if lesson.status == status_filter:
                        filtered_lessons.append(lesson)
                lessons = filtered_lessons
                
            serializer = LessonSerializer(lessons, many=True)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebLessonView.list exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=CreateLessonSerializer,
        responses={
            201: LessonSerializer,
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
            logging.getLogger().info("WebLessonView.create req=%s", request.data)
            
            serializer = CreateLessonSerializer(data=request.data)
            if not serializer.is_valid():
                return RestResponse(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST).response
            
            data = serializer.validated_data
            logging.getLogger().info("WebLessonView.create data=%s", data)

            if Lesson.objects.filter(
                module=data['module'],
                sequence_number=data['sequence_number'],
                deleted_at__isnull=True
            ).exists():
                return RestResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Lesson with this sequence number already exists"
                ).response
            
            if data['sequence_number'] > data['module'].total_lessons:
                return RestResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Sequence number cannot be greater than total lessons"
                ).response
            
            lesson = serializer.save()
            return RestResponse(data=LessonSerializer(lesson).data, status=status.HTTP_201_CREATED).response
        except Exception as e:
            logging.getLogger().exception("WebLessonView.create exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=UpdateLessonSerializer,
        responses={
            200: LessonSerializer,
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
    def update(self, request, pk=None):
        try:
            logging.getLogger().info("WebLessonView.update pk=%s", pk)
            
            lesson = Lesson.objects.filter(id=pk, deleted_at__isnull=True).first()
            if not lesson:
                return RestResponse(data={"error": "Lesson not found"}, status=status.HTTP_404_NOT_FOUND).response
            
            serializer = UpdateLessonSerializer(lesson, data=request.data, partial=True)
            if not serializer.is_valid():
                return RestResponse(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST).response
                
            serializer.save()
            return RestResponse(data=LessonSerializer(lesson).data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebLessonView.update exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        responses={
            204: 'No Content',
            404: openapi.Response(
                description='Not Found',
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
    @transaction.atomic
    def destroy(self, request, pk=None):
        try:
            logging.getLogger().info("WebLessonView.destroy pk=%s", pk)
            
            lesson = Lesson.objects.filter(id=pk, deleted_at__isnull=True).first()
            if not lesson:
                return RestResponse(data={"error": "Lesson not found"}, status=status.HTTP_404_NOT_FOUND).response
            
            module = lesson.module
            
            lesson.deleted_at = timezone.now()
            lesson.save()
            
            lessons_to_update = Lesson.objects.filter(
                module=module,
                sequence_number__gt=lesson.sequence_number,
                deleted_at__isnull=True
            ).order_by('sequence_number')
            
            for lesson_to_update in lessons_to_update:
                lesson_to_update.sequence_number -= 1
                lesson_to_update.save()
            
            module.total_lessons -= 1
            module.save(update_fields=['total_lessons'])
            
            return RestResponse(status=status.HTTP_204_NO_CONTENT).response
        except Exception as e:
            logging.getLogger().exception("WebLessonView.destroy exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response 
        
    @swagger_auto_schema(
        request_body=CreateLessonReplacementSerializer,
    )
    @action(detail=True, methods=['PATCH'], url_path='replace')
    def replace(self, request, pk=None):
        try:
            logging.getLogger().info("WebLessonView.replace pk=%s", pk)
            
            lesson = Lesson.objects.filter(id=pk, deleted_at__isnull=True).first()
            if not lesson:
                return RestResponse(message="Bài học không tồn tại", status=status.HTTP_404_NOT_FOUND).response
            
            if lesson.status != "not_started":
                return RestResponse(message="Không thể thay đổi lịch bài học đã bắt đầu hoặc đã kết thúc!", status=status.HTTP_400_BAD_REQUEST).response
            
            serializer = CreateLessonReplacementSerializer(data=request.data)
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response
            
            data = serializer.validated_data
            logging.getLogger().info("WebLessonView.replace data=%s", data)
            
            schedule : datetime = data['schedule']
            has_schedule = data['schedule'] is not None
            tz = ZoneInfo('Asia/Ho_Chi_Minh')
            
            if has_schedule and schedule < datetime.now(tz):
                return RestResponse(message="Thời gian thay thế không thể trước thời gian hiện tại!", status=status.HTTP_400_BAD_REQUEST).response
            
            previous_lesson = Lesson.objects.filter(
                module=lesson.module,
                sequence_number=lesson.sequence_number - 1,
                deleted_at__isnull=True
            ).order_by('sequence_number').first()
            
            previous_lesson_replacement = LessonReplacement.objects.filter(
                lesson=previous_lesson,
                deleted_at__isnull=True
            ).order_by('schedule').first()
            
            previous_lesson_end_datetime = None
            
            if previous_lesson_replacement:
                previous_lesson_end_datetime = previous_lesson_replacement.schedule
            elif previous_lesson:
                previous_lesson_end_datetime = previous_lesson.end_datetime
            
            if previous_lesson_end_datetime and schedule < previous_lesson_end_datetime + timedelta(minutes=30):
                return RestResponse(message="Thời gian học bù phải sau ít nhất 30 phút so với bài học trước!", status=status.HTTP_400_BAD_REQUEST).response
            
            next_lesson = Lesson.objects.filter(
                module=lesson.module,
                sequence_number=lesson.sequence_number + 1,
                deleted_at__isnull=True
            ).order_by('sequence_number').first()
            
            next_lesson_replacement = LessonReplacement.objects.filter(
                lesson=next_lesson,
                deleted_at__isnull=True
            ).order_by('schedule').first()
            
            next_lesson_start_datetime = None
            
            if next_lesson_replacement:
                next_lesson_start_datetime = next_lesson_replacement.schedule
            elif next_lesson:
                next_lesson_start_datetime = next_lesson.start_datetime
            
            if next_lesson_start_datetime and schedule > next_lesson_start_datetime - timedelta(hours=2):
                return RestResponse(message="Thời gian thay thế phải trước ít nhất 2 giờ so với bài học tiếp theo", status=status.HTTP_400_BAD_REQUEST).response
            
            LessonReplacement.objects.filter(
                lesson=lesson,
                deleted_at__isnull=True
            ).update(deleted_at=datetime.now())
            
            lesson_replacement = LessonReplacement.objects.create(
                lesson=lesson,
                schedule=data['schedule']
            )
            return RestResponse(data=LessonReplacementSerializer(lesson_replacement).data, status=status.HTTP_201_CREATED).response
        except Exception as e:
            logging.getLogger().exception("WebLessonView.replace exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response