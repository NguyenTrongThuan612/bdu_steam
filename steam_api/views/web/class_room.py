import logging
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.permissions import IsManager, IsNotRoot
from steam_api.models.class_room import ClassRoom
from steam_api.models.web_user import WebUserRole
from steam_api.serializers.class_room import (
    ClassRoomSerializer,
    CreateClassRoomSerializer,
    UpdateClassRoomSerializer
)
from steam_api.middlewares.web_authentication import WebUserAuthentication

class WebClassRoomView(viewsets.ViewSet):
    authentication_classes = (WebUserAuthentication,)
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy', 'set_thumbnail']:
            return [IsManager()]
        return [IsNotRoot()]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'course_id',
                openapi.IN_QUERY,
                description='Filter classes by course ID',
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'teacher',
                openapi.IN_QUERY,
                description='Filter classes by teacher or teaching assistant ID',
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: ClassRoomSerializer(many=True),
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
            logging.getLogger().info("WebClassRoomView.list params=%s", request.query_params)
            course_id = request.query_params.get('course_id')
            teacher_id = request.query_params.get('teacher')
            
            classes = ClassRoom.objects.filter(is_active=True, deleted_at__isnull=True)
            
            if course_id:
                classes = classes.filter(course_id=course_id)
            
            if teacher_id:
                classes = classes.filter(
                    Q(teacher_id=teacher_id) |
                    Q(teaching_assistant_id=teacher_id)
                )
            
            if request.user.role == WebUserRole.TEACHER:
                classes = classes.filter(teacher=request.user) | classes.filter(teaching_assistant=request.user)
                
            serializer = ClassRoomSerializer(classes, many=True)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebClassRoomView.list exc=%s, params=%s", e, request.query_params)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        responses={
            200: ClassRoomSerializer(),
            404: 'Not Found',
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
    def retrieve(self, request, pk=None):
        try:
            logging.getLogger().info("WebClassRoomView.retrieve pk=%s", pk)
            try:
                class_room = ClassRoom.objects.get(pk=pk, is_active=True, deleted_at__isnull=True)
            except ClassRoom.DoesNotExist:
                return RestResponse(status=status.HTTP_404_NOT_FOUND).response

            if request.user.role == WebUserRole.TEACHER:
                if class_room.teacher != request.user and class_room.teaching_assistant != request.user:
                    return RestResponse(status=status.HTTP_403_FORBIDDEN).response

            serializer = ClassRoomSerializer(class_room)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebClassRoomView.retrieve exc=%s, pk=%s", e, pk)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=CreateClassRoomSerializer,
        responses={
            201: ClassRoomSerializer(),
            400: 'Bad Request',
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
            logging.getLogger().info("WebClassRoomView.create req=%s", request.data)
            serializer = CreateClassRoomSerializer(data=request.data)
            
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response
            
            data = serializer.validated_data
            logging.getLogger().info("WebClassRoomView.create data=%s", data)
            
            if data['teaching_assistant'] and data['teacher'] and data['teaching_assistant'] == data['teacher']:
                return RestResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Teacher and teaching assistant cannot be the same person"
                ).response
            
            if data['start_date'] > data['end_date']:
                return RestResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Start date must be before end date"
                ).response
            
            if data['total_sessions'] < 0:
                return RestResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Total sessions cannot be negative"
                ).response

            class_room = serializer.save()
            response_serializer = ClassRoomSerializer(class_room)
            
            return RestResponse(data=response_serializer.data, status=status.HTTP_201_CREATED).response
        except Exception as e:
            logging.getLogger().exception("WebClassRoomView.create exc=%s, req=%s", e, request.data)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=UpdateClassRoomSerializer,
        responses={
            200: ClassRoomSerializer(),
            400: 'Bad Request',
            404: 'Not Found',
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
            logging.getLogger().info("WebClassRoomView.update pk=%s, req=%s", pk, request.data)
            try:
                class_room = ClassRoom.objects.get(pk=pk, deleted_at__isnull=True)
            except ClassRoom.DoesNotExist:
                return RestResponse(status=status.HTTP_404_NOT_FOUND).response

            serializer = UpdateClassRoomSerializer(class_room, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response
            
            data = serializer.validated_data
            logging.getLogger().info("WebClassRoomView.update data=%s", data)
            
            teacher = data.get('teacher', class_room.teacher if class_room else None)
            assistant = data.get('teaching_assistant', class_room.teaching_assistant if class_room else None)

            if teacher and assistant and teacher == assistant:
                return RestResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Teacher and teaching assistant cannot be the same person"
                ).response 
            
            if 'start_date' in data and 'end_date' in data:
                if data['start_date'] > data['end_date']:
                    return RestResponse(
                        status=status.HTTP_400_BAD_REQUEST,
                        message="Start date must be before end date"
                    ).response
            elif 'start_date' in data and class_room:
                if data['start_date'] > class_room.end_date:
                    return RestResponse(
                        status=status.HTTP_400_BAD_REQUEST,
                        message="Start date cannot be after current end date"
                    ).response
            elif 'end_date' in data and class_room:
                if class_room.start_date > data['end_date']:
                    return RestResponse(
                        status=status.HTTP_400_BAD_REQUEST,
                        message="End date cannot be before current start date"
                    ).response
                
            if 'total_sessions' in data and data['total_sessions'] < 0:
                return RestResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Total sessions cannot be negative"
                ).response

            updated_class = serializer.save()
            response_serializer = ClassRoomSerializer(updated_class)
            
            return RestResponse(data=response_serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebClassRoomView.update exc=%s, pk=%s, req=%s", e, pk, request.data)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        responses={
            204: 'No Content',
            404: 'Not Found',
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
    def destroy(self, request, pk=None):
        try:
            logging.getLogger().info("WebClassRoomView.destroy pk=%s", pk)
            try:
                class_room = ClassRoom.objects.get(pk=pk, deleted_at__isnull=True)
            except ClassRoom.DoesNotExist:
                return RestResponse(status=status.HTTP_404_NOT_FOUND).response

            class_room.is_active = False
            class_room.deleted_at = timezone.now()
            class_room.save(update_fields=['is_active', 'deleted_at'])
            
            return RestResponse(status=status.HTTP_204_NO_CONTENT).response
        except Exception as e:
            logging.getLogger().exception("WebClassRoomView.destroy exc=%s, pk=%s", e, pk)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'thumbnail',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='Class thumbnail image'
            )
        ],
        responses={
            200: ClassRoomSerializer(),
            400: 'Bad Request',
            404: 'Not Found',
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
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser], url_path='thumbnail')
    def set_thumbnail(self, request, pk=None):
        try:
            logging.getLogger().info("WebClassRoomView.set_thumbnail pk=%s", pk)
            try:
                class_room = ClassRoom.objects.get(pk=pk, deleted_at__isnull=True)
            except ClassRoom.DoesNotExist:
                return RestResponse(status=status.HTTP_404_NOT_FOUND).response

            if 'thumbnail' not in request.FILES:
                return RestResponse(
                    data={"error": "No thumbnail file provided"}, 
                    status=status.HTTP_400_BAD_REQUEST
                ).response

            class_room.thumbnail = request.FILES['thumbnail']
            class_room.save(update_fields=['thumbnail'])
            
            serializer = ClassRoomSerializer(class_room)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebClassRoomView.set_thumbnail exc=%s, pk=%s", e, pk)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response 