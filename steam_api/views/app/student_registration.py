import logging
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.app_authentication import AppAuthentication
from steam_api.models.student_registration_request import StudentRegistrationRequest
from steam_api.serializers.student_registration_request import (
    CreateStudentRegistrationRequestSerializer,
    StudentRegistrationRequestSerializer
)

class AppStudentRegistrationView(viewsets.ViewSet):
    authentication_classes = (AppAuthentication,)

    @swagger_auto_schema(
        responses={
            200: StudentRegistrationRequestSerializer(many=True),
            500: 'Internal Server Error'
        }
    )
    def list(self, request):
        try:
            logging.getLogger().info("AppStudentRegistrationView.list params=%s", request.query_params)
            
            requests = StudentRegistrationRequest.objects.filter(
                app_user=request.user,
                deleted_at__isnull=True
            ).order_by('-created_at')
            
            serializer = StudentRegistrationRequestSerializer(requests, many=True)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("AppStudentRegistrationView.list exc=%s, params=%s", e, request.query_params)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=CreateStudentRegistrationRequestSerializer,
        responses={
            201: CreateStudentRegistrationRequestSerializer(),
            400: 'Bad Request - Invalid data or duplicate request',
            500: 'Internal Server Error'
        }
    )
    def create(self, request):
        try:
            logging.getLogger().info("AppStudentRegistrationView.create req=%s", request.data)
            serializer = CreateStudentRegistrationRequestSerializer(data=request.data, context={'request': request})
            
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response
                
            registration_request = serializer.save()
            return RestResponse(
                data=serializer.data,
                message="Yêu cầu của bạn đã được ghi nhận và đang chờ xử lý!",
                status=status.HTTP_201_CREATED
            ).response
        except Exception as e:
            logging.getLogger().exception("AppStudentRegistrationView.create exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response 