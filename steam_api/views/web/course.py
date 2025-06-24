import logging
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.permissions import IsManager, IsNotRoot
from steam_api.models.course import Course
from steam_api.serializers.course import CourseSerializer, CreateCourseSerializer, UpdateCourseSerializer
from steam_api.middlewares.web_authentication import WebUserAuthentication

class WebCourseView(viewsets.ViewSet):
    authentication_classes = (WebUserAuthentication,)
    parser_classes = (MultiPartParser, FormParser)
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsManager()]
        return [IsNotRoot()]

    @swagger_auto_schema(
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
            logging.getLogger().info("WebCourseView.list params=%s", request.query_params)
            courses = Course.objects.filter(is_active=True, deleted_at__isnull=True)
            serializer = CourseSerializer(courses, many=True)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebCourseView.list exc=%s, params=%s", e, request.query_params)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        responses={
            200: CourseSerializer(),
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
            logging.getLogger().info("WebCourseView.retrieve pk=%s", pk)
            try:
                course = Course.objects.get(pk=pk, is_active=True, deleted_at__isnull=True)
            except Course.DoesNotExist:
                return RestResponse(status=status.HTTP_404_NOT_FOUND).response

            serializer = CourseSerializer(course)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebCourseView.retrieve exc=%s, pk=%s", e, pk)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=CreateCourseSerializer,
        manual_parameters=[
            openapi.Parameter(
                'thumbnail',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=False,
                description='Course thumbnail image'
            )
        ],
        responses={
            201: CourseSerializer(),
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
            logging.getLogger().info("WebCourseView.create req=%s", request.data)
            serializer = CreateCourseSerializer(data=request.data)
            
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response

            if 'thumbnail' in request.FILES:
                serializer.validated_data['thumbnail'] = request.FILES['thumbnail']

            course = serializer.save()
            response_serializer = CourseSerializer(course)
            
            return RestResponse(data=response_serializer.data, status=status.HTTP_201_CREATED).response
        except Exception as e:
            logging.getLogger().exception("WebCourseView.create exc=%s, req=%s", e, request.data)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=UpdateCourseSerializer,
        manual_parameters=[
            openapi.Parameter(
                'thumbnail',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=False,
                description='Course thumbnail image'
            )
        ],
        responses={
            200: CourseSerializer(),
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
            logging.getLogger().info("WebCourseView.update pk=%s, req=%s", pk, request.data)
            try:
                course = Course.objects.get(pk=pk, deleted_at__isnull=True)
            except Course.DoesNotExist:
                return RestResponse(status=status.HTTP_404_NOT_FOUND).response

            serializer = UpdateCourseSerializer(course, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response

            if 'thumbnail' in request.FILES:
                serializer.validated_data['thumbnail'] = request.FILES['thumbnail']

            updated_course = serializer.save()
            response_serializer = CourseSerializer(updated_course)
            
            return RestResponse(data=response_serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebCourseView.update exc=%s, pk=%s, req=%s", e, pk, request.data)
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
            logging.getLogger().info("WebCourseView.destroy pk=%s", pk)
            try:
                course = Course.objects.get(pk=pk, deleted_at__isnull=True)
            except Course.DoesNotExist:
                return RestResponse(status=status.HTTP_404_NOT_FOUND).response

            course.is_active = False
            course.deleted_at = timezone.now()
            course.save(update_fields=['is_active', 'deleted_at'])
            
            return RestResponse(status=status.HTTP_204_NO_CONTENT).response
        except Exception as e:
            logging.getLogger().exception("WebCourseView.destroy exc=%s, pk=%s", e, pk)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response 