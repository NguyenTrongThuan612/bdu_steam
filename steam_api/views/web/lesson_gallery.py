import logging
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.permissions import IsTeacher, IsNotRoot
from steam_api.models.lesson_gallery import LessonGallery
from steam_api.models.web_user import WebUserRole
from steam_api.serializers.lesson_gallery import (
    LessonGallerySerializer,
    CreateLessonGallerySerializer
)
from steam_api.middlewares.web_authentication import WebUserAuthentication

class WebLessonGalleryView(viewsets.ViewSet):
    authentication_classes = (WebUserAuthentication,)
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        if self.action in ['create']:
            return [IsTeacher()]
        return [IsNotRoot()]

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
            )
        ],
        responses={
            200: LessonGallerySerializer(many=True),
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
            logging.getLogger().info("WebLessonGalleryView.list params=%s", request.query_params)
            lesson_id = request.query_params.get('lesson')
            module_id = request.query_params.get('module')
            class_room_id = request.query_params.get('class_room')
            
            galleries = LessonGallery.objects.filter(deleted_at__isnull=True)

            if request.user.role == WebUserRole.TEACHER:
                galleries = galleries.filter(
                    Q(lesson__module__class_room__teacher=request.user) |
                    Q(lesson__module__class_room__teaching_assistant=request.user)
                )
            
            if lesson_id:
                galleries = galleries.filter(lesson_id=lesson_id)
                
            if module_id:
                galleries = galleries.filter(lesson__module_id=module_id)
                
            if class_room_id:
                galleries = galleries.filter(lesson__module__class_room_id=class_room_id)
                
            galleries = galleries.order_by('lesson__module__sequence_number', 'lesson__sequence_number')
                
            serializer = LessonGallerySerializer(galleries, many=True)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebLessonGalleryView.list exc=%s, params=%s", e, request.query_params)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        operation_description="Upload an image for a lesson. Maximum 5 images per lesson. Images will be stored in order of upload.",
        request_body=CreateLessonGallerySerializer,
        manual_parameters=[
            openapi.Parameter(
                'image',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='Lesson image (max 5 images per lesson)'
            )
        ],
        responses={
            201: LessonGallerySerializer(),
            400: 'Bad Request - Invalid data or max images reached',
            403: 'Forbidden - Not teacher of this class',
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
            logging.getLogger().info("WebLessonGalleryView.create req=%s", request.data)
            serializer = CreateLessonGallerySerializer(data=request.data)
            
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response

            data = serializer.validated_data
            logging.getLogger().info("WebLessonGalleryView.create data=%s", data)

            lesson = data['lesson']
            
            if request.user not in [lesson.module.class_room.teacher, lesson.module.class_room.teaching_assistant]:
                return RestResponse(
                    status=status.HTTP_403_FORBIDDEN,
                    message="You are not the teacher of this class"
                ).response
            
            gallery = LessonGallery.objects.filter(
                lesson=data['lesson'],
                deleted_at__isnull=True
            ).first()
            
            if gallery and gallery.images_count >= 5:
                return RestResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="This lesson already has maximum number of images (5)"
                ).response 

            if 'image' not in request.FILES:
                return RestResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Image is required"
                ).response

            serializer.validated_data['image'] = request.FILES['image']
            gallery = serializer.save()
            
            response_serializer = LessonGallerySerializer(gallery)
            return RestResponse(data=response_serializer.data, status=status.HTTP_201_CREATED).response
        except Exception as e:
            logging.getLogger().exception("WebLessonGalleryView.create exc=%s, req=%s", e, request.data)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response 