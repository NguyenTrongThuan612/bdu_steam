import logging
from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.permissions import IsManager, IsNotRoot
from steam_api.models.student import Student
from steam_api.models.web_user import WebUserRole
from steam_api.serializers.student import (
    StudentSerializer,
    CreateStudentSerializer,
    UpdateStudentSerializer
)
from steam_api.middlewares.web_authentication import WebUserAuthentication

class WebStudentView(viewsets.ViewSet):
    authentication_classes = (WebUserAuthentication,)
    parser_classes = (MultiPartParser, FormParser)
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsManager()]
        return [IsNotRoot()]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description='Search students by identification number, name, phone, parent info',
                type=openapi.TYPE_STRING,
                required=False
            )
        ],
        responses={
            200: StudentSerializer(many=True),
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
            logging.getLogger().info("WebStudentView.list params=%s", request.query_params)
            search = request.query_params.get('search', '')
            
            students = Student.objects.filter(deleted_at__isnull=True)

            if request.user.role == WebUserRole.TEACHER:
                students = students.filter(
                    Q(course_registrations__class_room__teacher=request.user) |
                    Q(course_registrations__class_room__teaching_assistant=request.user)
                )
            
            if search:
                students = students.filter(
                    Q(identification_number__icontains=search) |
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search) |
                    Q(phone_number__icontains=search) |
                    Q(parent_name__icontains=search) |
                    Q(parent_phone__icontains=search)
                )
                
            serializer = StudentSerializer(students, many=True)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebStudentView.list exc=%s, params=%s", e, request.query_params)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        responses={
            200: StudentSerializer(),
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
            logging.getLogger().info("WebStudentView.retrieve pk=%s", pk)
            try:
                student = Student.objects.get(pk=pk, deleted_at__isnull=True)
                if request.user.role == WebUserRole.TEACHER:
                    if student not in request.user.teaching_classes.students.all() and student not in request.user.assisting_classes.students.all():
                        return RestResponse(status=status.HTTP_403_FORBIDDEN).response
            except Student.DoesNotExist:
                return RestResponse(status=status.HTTP_404_NOT_FOUND).response

            serializer = StudentSerializer(student)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebStudentView.retrieve exc=%s, pk=%s", e, pk)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=CreateStudentSerializer,
        manual_parameters=[
            openapi.Parameter(
                'avatar',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=False,
                description='Student avatar image'
            )
        ],
        responses={
            201: StudentSerializer(),
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
            logging.getLogger().info("WebStudentView.create req=%s", request.data)
            serializer = CreateStudentSerializer(data=request.data)
            
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response

            if 'avatar' in request.FILES:
                serializer.validated_data['avatar'] = request.FILES['avatar']

            student = serializer.save()
            response_serializer = StudentSerializer(student)
            
            return RestResponse(data=response_serializer.data, status=status.HTTP_201_CREATED).response
        except Exception as e:
            logging.getLogger().exception("WebStudentView.create exc=%s, req=%s", e, request.data)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=UpdateStudentSerializer,
        manual_parameters=[
            openapi.Parameter(
                'avatar',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=False,
                description='Student avatar image'
            )
        ],
        responses={
            200: StudentSerializer(),
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
            logging.getLogger().info("WebStudentView.update pk=%s, req=%s", pk, request.data)
            try:
                student = Student.objects.get(pk=pk, deleted_at__isnull=True)
            except Student.DoesNotExist:
                return RestResponse(status=status.HTTP_404_NOT_FOUND).response

            serializer = UpdateStudentSerializer(student, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response

            if 'avatar' in request.FILES:
                serializer.validated_data['avatar'] = request.FILES['avatar']

            updated_student = serializer.save()
            response_serializer = StudentSerializer(updated_student)
            
            return RestResponse(data=response_serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebStudentView.update exc=%s, pk=%s, req=%s", e, pk, request.data)
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
            logging.getLogger().info("WebStudentView.destroy pk=%s", pk)
            try:
                student = Student.objects.get(pk=pk, deleted_at__isnull=True)
            except Student.DoesNotExist:
                return RestResponse(status=status.HTTP_404_NOT_FOUND).response

            student.is_active = False
            student.deleted_at = timezone.now()
            student.save(update_fields=['is_active', 'deleted_at'])
            
            return RestResponse(status=status.HTTP_204_NO_CONTENT).response
        except Exception as e:
            logging.getLogger().exception("WebStudentView.destroy exc=%s, pk=%s", e, pk)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response 