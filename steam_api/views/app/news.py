from rest_framework import viewsets, status
from steam_api.models.news import News
from steam_api.serializers.news import NewsSerializer
from steam_api.middlewares.app_authentication import AppAuthentication
from steam_api.helpers.response import RestResponse
from drf_yasg.utils import swagger_auto_schema
import logging

class AppNewsView(viewsets.ViewSet):
    authentication_classes = (AppAuthentication,)

    @swagger_auto_schema(
        operation_description="Get all news",
        responses={200: NewsSerializer(many=True)}
    )
    def list(self, request):
        try:
            logging.getLogger().info("AppNewsView.list params=%s", request.query_params)
            news = News.objects.filter(deleted_at__isnull=True).order_by('-posted_at')
            serializer = NewsSerializer(news, many=True)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("AppNewsView.list exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response
        
        