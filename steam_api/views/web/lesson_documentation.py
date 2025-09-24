import logging
from datetime import datetime
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from steam_api.helpers.response import RestResponse
from steam_api.models.lesson_documentation import LessonDocumentation
from steam_api.middlewares.permissions import IsManager, IsNotRoot
from steam_api.serializers.lesson_documentation import LessonDocumentationSerializer, CreateLessonDocumentationSerializer, UpdateLessonDocumentationSerializer
from steam_api.middlewares.web_authentication import WebUserAuthentication

class WebLessonDocumentationView(viewsets.ViewSet):
    authentication_classes = (WebUserAuthentication,)

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsManager()]
        return [IsNotRoot()]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'lesson',
                openapi.IN_QUERY,
                description='Filter by lesson ID',
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: LessonDocumentationSerializer(many=True)
        }
    )
    def list(self, request):
        try:
            logging.getLogger().info("WebLessonDocumentationView.list req=%s", request.query_params)
            lesson_documentations = LessonDocumentation.objects.filter(deleted_at__isnull=True)
            lesson_param = request.query_params.get('lesson')
            if lesson_param:
                lesson_documentations = lesson_documentations.filter(lesson=lesson_param)
            serializer = LessonDocumentationSerializer(lesson_documentations, many=True, context={'request': request})
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebLessonDocumentationView.list exc=%s, req=%s", e, request.query_params)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        responses={
            200: LessonDocumentationSerializer
        }
    )
    def retrieve(self, request, pk=None):
        try:
            logging.getLogger().info("WebLessonDocumentationView.retrieve pk=%s, req=%s", pk, request.query_params)
            lesson_documentation = LessonDocumentation.objects.get(pk=pk, deleted_at__isnull=True)
            serializer = LessonDocumentationSerializer(lesson_documentation)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except LessonDocumentation.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND).response
        except Exception as e:
            logging.getLogger().exception("WebLessonDocumentationView.retrieve exc=%s, pk=%s, req=%s", e, pk, request.query_params)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=CreateLessonDocumentationSerializer,
        responses={
            201: LessonDocumentationSerializer
        }
    )
    def create(self, request):
        try:
            logging.getLogger().info("WebLessonDocumentationView.create req=%s", request.data)
            serializer = CreateLessonDocumentationSerializer(data=request.data)

            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response

            data = serializer.validated_data
            logging.getLogger().info("WebLessonDocumentationView.create data=%s", data)
            lesson_documentation = serializer.save()
            return RestResponse(data=LessonDocumentationSerializer(lesson_documentation).data, status=status.HTTP_201_CREATED).response
        except Exception as e:
            logging.getLogger().exception("WebLessonDocumentationView.create exc=%s, req=%s", e, request.data)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    
    @swagger_auto_schema(
        request_body=UpdateLessonDocumentationSerializer,
        responses={
            200: LessonDocumentationSerializer
        }
    )
    def update(self, request, pk=None):
        try:
            logging.getLogger().info("WebLessonDocumentationView.update pk=%s, req=%s", pk, request.data)
            lesson_documentation = LessonDocumentation.objects.get(pk=pk, deleted_at__isnull=True)
            serializer = UpdateLessonDocumentationSerializer(lesson_documentation, data=request.data, partial=True)

            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response

            data = serializer.validated_data
            logging.getLogger().info("WebLessonDocumentationView.update data=%s", data)
            lesson_documentation = serializer.save()
            return RestResponse(data=LessonDocumentationSerializer(lesson_documentation).data, status=status.HTTP_200_OK).response
        except LessonDocumentation.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND).response
        except Exception as e:
            logging.getLogger().exception("WebLessonDocumentationView.update exc=%s, pk=%s, req=%s", e, pk, request.data)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        responses={
            204: 'No Content'
        }
    )
    def destroy(self, request, pk=None):
        try:
            logging.getLogger().info("WebLessonDocumentationView.destroy pk=%s, req=%s", pk, request.query_params)
            lesson_documentation = LessonDocumentation.objects.get(pk=pk, deleted_at__isnull=True)
            lesson_documentation.deleted_at = datetime.now()
            lesson_documentation.save()
            return RestResponse(status=status.HTTP_204_NO_CONTENT).response
        except LessonDocumentation.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND).response
        except Exception as e:
            logging.getLogger().exception("WebLessonDocumentationView.destroy exc=%s, pk=%s, req=%s", e, pk, request.query_params)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response
