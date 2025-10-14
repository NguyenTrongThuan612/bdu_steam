import logging
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.app_authentication import AppAuthentication
from steam_api.models.student_registration import StudentRegistration, StudentRegistrationStatus
from steam_api.models.student import Student
from steam_api.serializers.student_registration import (
    CreateStudentRegistrationSerializer,
    StudentRegistrationSerializer
)
class AppStudentRegistrationView(viewsets.ViewSet):
    authentication_classes = (AppAuthentication,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description='Filter by status (pending/approved/rejected)',
                type=openapi.TYPE_STRING,
                required=False,
                enum=[status.value for status in StudentRegistrationStatus]
            )
        ],
        responses={
            200: StudentRegistrationSerializer(many=True),
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
            logging.getLogger().info("AppStudentRegistrationView.list params=%s", request.query_params)
            
            status_filter = request.query_params.get('status')
            
            requests = StudentRegistration.objects.filter(
                app_user=request.user,
                deleted_at__isnull=True
            )
            
            if status_filter and status_filter in [status.value for status in StudentRegistrationStatus]:
                requests = requests.filter(status=status_filter)
            
            requests = requests.order_by('-created_at')
            
            serializer = StudentRegistrationSerializer(requests, many=True)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("AppStudentRegistrationView.list exc=%s, params=%s", e, request.query_params)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=CreateStudentRegistrationSerializer,
        responses={
            201: CreateStudentRegistrationSerializer(),
            400: 'Bad Request - Invalid data or duplicate request',
            500: 'Internal Server Error'
        }
    )
    def create(self, request):
        try:
            logging.getLogger().info("AppStudentRegistrationView.create req=%s", request.data)
            serializer = CreateStudentRegistrationSerializer(data=request.data)
            
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST, message="Dữ liệu không hợp lệ!").response
                
            student = Student.objects.get(
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                date_of_birth=serializer.validated_data['date_of_birth'],
                identification_number=serializer.validated_data['identification_number']
            )
            StudentRegistration.objects.create(
                app_user=request.user,
                student=student,
                status=StudentRegistrationStatus.PENDING
            )

            return RestResponse(
                data=serializer.data,
                message="Yêu cầu của bạn đã được ghi nhận và đang chờ xử lý!",
                status=status.HTTP_201_CREATED
            ).response
        except Exception as e:
            logging.getLogger().exception("AppStudentRegistrationView.create exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response 