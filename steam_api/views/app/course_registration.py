import logging
from django.utils import timezone
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from steam_api.helpers.response import RestResponse
from steam_api.models.course_registration import CourseRegistration
from steam_api.models.student_registration import StudentRegistration, StudentRegistrationStatus
from steam_api.serializers.course_registration import (
    CourseRegistrationSerializer,
    CreateCourseRegistrationSerializer,
)
from steam_api.middlewares.app_authentication import AppAuthentication

class AppCourseRegistrationView(viewsets.ViewSet):
    authentication_classes = (AppAuthentication,)
    
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
            logging.getLogger().info("AppCourseRegistrationView.list params=%s", request.query_params)
            student_id = request.query_params.get('student')
            class_room_id = request.query_params.get('class_room')
            status_param = request.query_params.get('status')

            valid_students = StudentRegistration.objects.filter(
                app_user=request.user,
                status=StudentRegistrationStatus.APPROVED,
                deleted_at__isnull=True
            )
            
            registrations = CourseRegistration.objects.filter(deleted_at__isnull=True, student__in=valid_students)
            
            if student_id:
                registrations = registrations.filter(student_id=student_id)
                
            if class_room_id:
                registrations = registrations.filter(class_room_id=class_room_id)
                
            if status_param:
                registrations = registrations.filter(status=status_param)
                
            registrations = registrations.order_by('-created_at')
                
            serializer = CourseRegistrationSerializer(registrations, many=True)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("AppCourseRegistrationView.list exc=%s, params=%s", e, request.query_params)
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
            logging.getLogger().info("AppCourseRegistrationView.create req=%s", request.data)
            serializer = CreateCourseRegistrationSerializer(data=request.data, context={'allow_anonymous': True})
            
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response

            data = serializer.validated_data
            logging.getLogger().info("AppCourseRegistrationView.create data=%s", data)
            
            if data['student'].course_registrations.filter(class_room=data['class_room'], deleted_at__isnull=True).exists():
                return RestResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Student has already registered for this class"
                ).response
            
            if data['class_room'].current_students_count >= data['class_room'].max_students:
                return RestResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Class is full"
                ).response

            valid_students = StudentRegistration.objects.filter(
                app_user=request.user,
                status=StudentRegistrationStatus.APPROVED,
                deleted_at__isnull=True
            )

            if not valid_students.filter(student=data['student']).exists():
                return RestResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="You are not allowed to register for this student"
                ).response

            data["status"] = "pending"
            registration = serializer.save()
            response_serializer = CourseRegistrationSerializer(registration)
            
            return RestResponse(data=response_serializer.data, status=status.HTTP_201_CREATED).response
        except Exception as e:
            logging.getLogger().exception("AppCourseRegistrationView.create exc=%s, req=%s", e, request.data)
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
            logging.getLogger().info("AppCourseRegistrationView.destroy pk=%s", pk)
            try:
                registration = CourseRegistration.objects.get(pk=pk, deleted_at__isnull=True)
            except CourseRegistration.DoesNotExist:
                return RestResponse(status=status.HTTP_404_NOT_FOUND).response

            registration.deleted_at = timezone.now()
            registration.save(update_fields=['deleted_at'])
            
            return RestResponse(status=status.HTTP_204_NO_CONTENT).response
        except Exception as e:
            logging.getLogger().exception("AppCourseRegistrationView.destroy exc=%s, pk=%s", e, pk)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response 