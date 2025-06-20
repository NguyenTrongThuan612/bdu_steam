import logging
from rest_framework.views import APIView
from rest_framework import status
from django.db import connection
from django.db.utils import OperationalError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone

from steam_api.helpers.response import RestResponse

class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description='System is healthy',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'database': openapi.Schema(type=openapi.TYPE_STRING),
                        'timestamp': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            503: openapi.Response(
                description='Service Unavailable',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def get(self, request):
        logging.getLogger().info("HealthCheckView.get")
        
        return RestResponse(
            status=status.HTTP_200_OK
        ).response
