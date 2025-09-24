from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser
from steam_api.models.news import News
from steam_api.serializers.news import NewsSerializer, CreateNewsSerializer, UpdateNewsSerializer
from steam_api.middlewares.web_authentication import WebUserAuthentication
from steam_api.middlewares.permissions import IsManager, IsNotRoot
from steam_api.helpers.response import RestResponse
from drf_yasg.utils import swagger_auto_schema
import logging
from steam_api.helpers.local_storage import upload_file_to_local
from datetime import datetime
from rest_framework.request import Request

class WebNewsView(viewsets.ViewSet):
    authentication_classes = (WebUserAuthentication,)
    parser_classes = (MultiPartParser,)

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsNotRoot()]
        return [IsManager()]

    @swagger_auto_schema(
        operation_description="Get all news",
        responses={200: NewsSerializer(many=True)}
    )
    def list(self, request: Request):
        try:
            logging.getLogger().info("WebNewsView.list params=%s", request.query_params)
            news = News.objects.filter(deleted_at__isnull=True).order_by('-posted_at')
            serializer = NewsSerializer(news, many=True, context={'request': request})
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebNewsView.list exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        operation_description="Create a new news",
        request_body=CreateNewsSerializer,
        responses={201: NewsSerializer}
    )
    def create(self, request):
        try:
            logging.getLogger().info("WebNewsView.create req=%s", request.data)
            serializer = CreateNewsSerializer(data=request.data)
            if not serializer.is_valid():
                return RestResponse(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST).response

            image = serializer.validated_data.pop('image')
            image_url = upload_file_to_local(image)
            news = News.objects.create(
                title=serializer.validated_data['title'],
                link=serializer.validated_data['link'],
                image=image_url,
                posted_at=serializer.validated_data['posted_at']
            )
            
            return RestResponse(data=NewsSerializer(news, context={'request': request}).data, status=status.HTTP_201_CREATED).response
        except Exception as e:
            logging.getLogger().exception("WebNewsView.create exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        operation_description="Update a news",
        request_body=UpdateNewsSerializer,
        responses={200: NewsSerializer}
    )
    def update(self, request, pk=None):
        try:
            logging.getLogger().info("WebNewsView.update req=%s", request.data)
            serializer = UpdateNewsSerializer(data=request.data)

            if not serializer.is_valid():
                return RestResponse(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST).response

            news = News.objects.get(id=pk)

            validated_data = serializer.validated_data

            if "image" in validated_data:
                image_url = upload_file_to_local(validated_data.pop('image'))
                news.image = image_url

            for key, value in validated_data.items():
                setattr(news, key, value)

            news.save()

            return RestResponse(data=NewsSerializer(news, context={'request': request}).data, status=status.HTTP_200_OK).response
        except News.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND).response
        except Exception as e:
            logging.getLogger().exception("WebNewsView.update exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    def destroy(self, request, pk=None):
        try:
            logging.getLogger().info("WebNewsView.destroy pk=%s", pk)
            news = News.objects.get(id=pk)
            news.deleted_at = datetime.now()
            news.save()
            return RestResponse(status=status.HTTP_200_OK).response
        except News.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND).response
        except Exception as e:
            logging.getLogger().exception("WebNewsView.destroy exc=%s", e)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response
        
        