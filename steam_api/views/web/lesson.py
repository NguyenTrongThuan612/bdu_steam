import logging
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from django.db import transaction

from steam_api.helpers.response import RestResponse
from steam_api.models.lesson import Lesson
from steam_api.serializers.lesson import LessonSerializer, UpdateLessonSerializer, CreateLessonSerializer
from steam_api.middlewares.permissions import IsManager
from steam_api.middlewares.web_authentication import WebUserAuthentication

class WebLessonView(viewsets.ViewSet):
    authentication_classes = (WebUserAuthentication,)
    permission_classes = (IsManager,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'module',
                openapi.IN_QUERY,
                description='Filter lessons by module ID',
                type=openapi.TYPE_INTEGER,
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
            logging.getLogger().info("WebLessonView.list")
            module_id = request.query_params.get('module')
            
            # Get lessons that are not deleted
            lessons = Lesson.objects.filter(deleted_at__isnull=True)
            
            if module_id:
                lessons = lessons.filter(module_id=module_id)
                
            # Order by module sequence number and lesson sequence number
            lessons = lessons.order_by('module__sequence_number', 'sequence_number')
                
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
            logging.getLogger().info("WebLessonView.create")
            
            serializer = CreateLessonSerializer(data=request.data)
            if not serializer.is_valid():
                return RestResponse(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST).response
                
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
            
            # Soft delete the lesson
            lesson.deleted_at = timezone.now()
            lesson.save()
            
            # Update sequence numbers of remaining lessons
            lessons_to_update = Lesson.objects.filter(
                module=module,
                sequence_number__gt=lesson.sequence_number,
                deleted_at__isnull=True
            ).order_by('sequence_number')
            
            for lesson_to_update in lessons_to_update:
                lesson_to_update.sequence_number -= 1
                lesson_to_update.save()
            
            # Update module's total_lessons
            module.total_lessons -= 1
            module.save(update_fields=['total_lessons'])
            
            return RestResponse(status=status.HTTP_204_NO_CONTENT).response
        except Exception as e:
            logging.getLogger().exception("WebLessonView.destroy exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response 