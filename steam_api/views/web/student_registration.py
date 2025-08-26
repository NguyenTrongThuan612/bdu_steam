import logging
from django.utils import timezone
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.web_authentication import WebUserAuthentication
from steam_api.middlewares.permissions import IsManager
from steam_api.models.student_registration import StudentRegistration, StudentRegistrationStatus
from steam_api.serializers.student_registration import (
    StudentRegistrationSerializer,
    UpdateStudentRegistrationStatusSerializer
)

class WebStudentRegistrationView(viewsets.ViewSet):
    authentication_classes = (WebUserAuthentication,)
    permission_classes = (IsManager,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description='Filter by request status',
                type=openapi.TYPE_STRING,
                enum=StudentRegistrationStatus.values,
                required=False
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description='Search by name or identification number',
                type=openapi.TYPE_STRING,
                required=False
            )
        ],
        responses={
            200: StudentRegistrationSerializer(many=True),
            500: 'Internal Server Error'
        }
    )
    def list(self, request):
        try:
            logging.getLogger().info("WebStudentRegistrationView.list params=%s", request.query_params)
            status_param = request.query_params.get('status')
            search = request.query_params.get('search', '')
            
            requests = StudentRegistration.objects.filter(deleted_at__isnull=True)
            
            if status_param:
                requests = requests.filter(status=status_param)
                
            if search:
                requests = requests.filter(
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search) |
                    Q(identification_number__icontains=search)
                )
                
            requests = requests.order_by('-created_at')
                
            serializer = StudentRegistrationSerializer(requests, many=True)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebStudentRegistrationView.list exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=UpdateStudentRegistrationStatusSerializer,
        responses={
            200: StudentRegistrationSerializer(),
            400: 'Bad Request - Invalid data',
            404: 'Not Found',
            500: 'Internal Server Error'
        }
    )
    def update(self, request, pk=None):
        try:
            logging.getLogger().info("WebStudentRegistrationView.update pk=%s, req=%s", pk, request.data)
            
            try:
                registration_request = StudentRegistration.objects.get(
                    pk=pk,
                    deleted_at__isnull=True,
                    status=StudentRegistrationStatus.PENDING
                )
            except StudentRegistration.DoesNotExist:
                return RestResponse(
                    message="Registration request not found or already processed",
                    status=status.HTTP_404_NOT_FOUND
                ).response
            
            serializer = UpdateStudentRegistrationStatusSerializer(
                registration_request,
                data=request.data,
                partial=True
            )
            
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response
            
            data = serializer.validated_data
            logging.getLogger().info("WebStudentRegistrationView.update data=%s", data)

            if data.get('status', None) not in [StudentRegistrationStatus.APPROVED.value, StudentRegistrationStatus.REJECTED.value]:
                return RestResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Status must be either approved or rejected" 
                ).response
                
            updated_request = serializer.save()
            response_serializer = StudentRegistrationSerializer(updated_request)
            
            return RestResponse(
                data=response_serializer.data,
                message="Registration request updated successfully",
                status=status.HTTP_200_OK
            ).response
        except Exception as e:
            logging.getLogger().exception("WebStudentRegistrationView.update exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response 