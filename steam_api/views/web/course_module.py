import logging
from django.utils import timezone
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.permissions import IsManager, IsNotRoot
from steam_api.models.course_module import CourseModule
from steam_api.serializers.course_module import (
    CourseModuleSerializer,
    CreateCourseModuleSerializer,
    UpdateCourseModuleSerializer,
    ListCourseModuleSerializer
)
from steam_api.middlewares.web_authentication import WebUserAuthentication

class WebCourseModuleView(viewsets.ViewSet):
    authentication_classes = (WebUserAuthentication,)

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsManager()]
        return [IsNotRoot()]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'class_room',
                openapi.IN_QUERY,
                description='Filter modules by class room ID',
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: ListCourseModuleSerializer(many=True),
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
            logging.getLogger().info("WebCourseModuleView.list")
            class_room_id = request.query_params.get('class_room')
            
            modules = CourseModule.objects.filter(
                class_room__teacher=request.user,
                deleted_at__isnull=True
            ) | CourseModule.objects.filter(
                class_room__teaching_assistant=request.user,
                deleted_at__isnull=True
            )
            
            if class_room_id:
                modules = modules.filter(class_room_id=class_room_id)
                
            modules = modules.order_by('sequence_number')
                
            serializer = ListCourseModuleSerializer(modules, many=True)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebCourseModuleView.list exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=CreateCourseModuleSerializer,
        responses={
            201: CourseModuleSerializer(),
            400: 'Bad Request',
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
            logging.getLogger().info("WebCourseModuleView.create req=%s", request.data)
            serializer = CreateCourseModuleSerializer(data=request.data)
            
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response

            module = serializer.save()
            response_serializer = CourseModuleSerializer(module)
            return RestResponse(data=response_serializer.data, status=status.HTTP_201_CREATED).response
        except Exception as e:
            logging.getLogger().exception("WebCourseModuleView.create exc=%s, req=%s", e, request.data)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=UpdateCourseModuleSerializer,
        responses={
            200: CourseModuleSerializer(),
            400: 'Bad Request',
            403: 'Forbidden - Not teacher of this class',
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
            logging.getLogger().info("WebCourseModuleView.update pk=%s, req=%s", pk, request.data)
            try:
                module = CourseModule.objects.get(pk=pk, deleted_at__isnull=True)
            except CourseModule.DoesNotExist:
                return RestResponse(status=status.HTTP_404_NOT_FOUND).response

            serializer = UpdateCourseModuleSerializer(module, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response

            updated_module = serializer.save()
            response_serializer = CourseModuleSerializer(updated_module)
            return RestResponse(data=response_serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebCourseModuleView.update exc=%s, pk=%s, req=%s", e, pk, request.data)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        responses={
            204: 'No Content',
            403: 'Forbidden - Not teacher of this class',
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
            logging.getLogger().info("WebCourseModuleView.destroy pk=%s", pk)
            try:
                module = CourseModule.objects.get(pk=pk, deleted_at__isnull=True)
            except CourseModule.DoesNotExist:
                return RestResponse(status=status.HTTP_404_NOT_FOUND).response

            module.deleted_at = timezone.now()
            module.save(update_fields=['deleted_at'])
            
            return RestResponse(status=status.HTTP_204_NO_CONTENT).response
        except Exception as e:
            logging.getLogger().exception("WebCourseModuleView.destroy exc=%s, pk=%s", e, pk)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response 