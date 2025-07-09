import logging
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.permissions import IsNotRoot
from steam_api.models.course import Course
from steam_api.serializers.course import CourseSerializer
from steam_api.middlewares.app_authentication import AppAuthentication  

class AppCourseView(viewsets.ViewSet):
    authentication_classes = (AppAuthentication,)
    
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
            logging.getLogger().info("AppCourseView.list")
            
            courses = Course.objects.filter(deleted_at__isnull=True, is_active=True)
            
            serializer = CourseSerializer(courses, many=True)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("AppCourseView.list exc=%s, params=%s", e, request.query_params)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response 