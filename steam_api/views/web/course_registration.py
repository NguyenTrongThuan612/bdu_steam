import logging
from django.utils import timezone
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.permissions import IsManager, IsNotRoot
from steam_api.models.course_registration import CourseRegistration
from steam_api.models.web_user import WebUserRole
from steam_api.serializers.course_registration import (
    CourseRegistrationSerializer,
    CreateCourseRegistrationSerializer,
    UpdateCourseRegistrationSerializer
)
from steam_api.middlewares.web_authentication import WebUserAuthentication

class WebCourseRegistrationView(viewsets.ViewSet):
    authentication_classes = (WebUserAuthentication,)
    
    def get_permissions(self):
        if self.action in ['update', 'destroy']:
            return [IsManager()]
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
                'class_room',
                openapi.IN_QUERY,
                description='Filter by class room ID',
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description='Filter by registration status',
                type=openapi.TYPE_STRING,
                enum=['pending', 'approved', 'rejected', 'cancelled'],
                required=False
            )
        ],
        responses={
            200: CourseRegistrationSerializer(many=True),
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
            logging.getLogger().info("WebCourseRegistrationView.list")
            student_id = request.query_params.get('student')
            class_room_id = request.query_params.get('class_room')
            status = request.query_params.get('status')
            
            registrations = CourseRegistration.objects.filter(deleted_at__isnull=True)
            
            if student_id:
                registrations = registrations.filter(student_id=student_id)
                
            if class_room_id:
                registrations = registrations.filter(class_room_id=class_room_id)
                
            if status:
                registrations = registrations.filter(status=status)
                
            # Sắp xếp theo thời gian tạo, mới nhất lên đầu
            registrations = registrations.order_by('-created_at')
                
            serializer = CourseRegistrationSerializer(registrations, many=True)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebCourseRegistrationView.list exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=CreateCourseRegistrationSerializer,
        responses={
            201: CourseRegistrationSerializer(),
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
            logging.getLogger().info("WebCourseRegistrationView.create req=%s", request.data)
            serializer = CreateCourseRegistrationSerializer(data=request.data)
            
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response

            registration = serializer.save()
            response_serializer = CourseRegistrationSerializer(registration)
            
            return RestResponse(data=response_serializer.data, status=status.HTTP_201_CREATED).response
        except Exception as e:
            logging.getLogger().exception("WebCourseRegistrationView.create exc=%s, req=%s", e, request.data)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=UpdateCourseRegistrationSerializer,
        responses={
            200: CourseRegistrationSerializer(),
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
            logging.getLogger().info("WebCourseRegistrationView.update pk=%s, req=%s", pk, request.data)
            try:
                registration = CourseRegistration.objects.get(pk=pk, deleted_at__isnull=True)
            except CourseRegistration.DoesNotExist:
                return RestResponse(status=status.HTTP_404_NOT_FOUND).response

            serializer = UpdateCourseRegistrationSerializer(registration, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response

            updated_registration = serializer.save()
            response_serializer = CourseRegistrationSerializer(updated_registration)
            
            return RestResponse(data=response_serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebCourseRegistrationView.update exc=%s, pk=%s, req=%s", e, pk, request.data)
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
            logging.getLogger().info("WebCourseRegistrationView.destroy pk=%s", pk)
            try:
                registration = CourseRegistration.objects.get(pk=pk, deleted_at__isnull=True)
            except CourseRegistration.DoesNotExist:
                return RestResponse(status=status.HTTP_404_NOT_FOUND).response

            # Soft delete
            registration.deleted_at = timezone.now()
            registration.save(update_fields=['deleted_at'])
            
            return RestResponse(status=status.HTTP_204_NO_CONTENT).response
        except Exception as e:
            logging.getLogger().exception("WebCourseRegistrationView.destroy exc=%s, pk=%s", e, pk)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response 