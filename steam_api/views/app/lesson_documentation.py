import logging
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.app_authentication import AppAuthentication
from steam_api.models.lesson_documentation import LessonDocumentation
from steam_api.serializers.lesson_documentation import LessonDocumentationSerializer

class AppLessonDocumentationView(viewsets.ViewSet):
    authentication_classes = (AppAuthentication,)

    @swagger_auto_schema(
        responses={
            200: LessonDocumentationSerializer(many=True)
        },
        manual_parameters=[
            openapi.Parameter(
                'lesson',
                openapi.IN_QUERY,
                description='Filter by lesson ID',
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
    )
    def list(self, request):
        try:
            logging.getLogger().info("AppLessonDocumentationView.list req=%s", request.query_params)
            lesson_documentations = LessonDocumentation.objects.filter(deleted_at__isnull=True)
            lesson_param = request.query_params.get('lesson')
            if lesson_param:
                lesson_documentations = lesson_documentations.filter(lesson=lesson_param)
            serializer = LessonDocumentationSerializer(lesson_documentations, many=True, context={'request': request})
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("AppLessonDocumentationView.list exc=%s, req=%s", e, request.query_params)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response