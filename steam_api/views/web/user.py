import logging
from django.db.models import Q
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.web_authentication import WebUserAuthentication
from steam_api.middlewares.permissions import IsNotRoot
from steam_api.models.web_user import WebUser, WebUserRole, WebUserStatus
from steam_api.serializers.web_user import WebUserSerializer

class UserView(viewsets.ViewSet):
    authentication_classes = (WebUserAuthentication,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'role',
                openapi.IN_QUERY,
                description='Filter users by role',
                type=openapi.TYPE_STRING,
                enum=WebUserRole.values,
                required=False
            ),
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description='Filter users by status',
                type=openapi.TYPE_STRING,
                enum=WebUserStatus.values,
                required=False
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description='Search users by email or phone',
                type=openapi.TYPE_STRING,
                required=False
            )
        ],
        responses={
            200: WebUserSerializer(many=True),
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
            logging.getLogger().info("UserView.list params=%s", request.query_params)
            role = request.query_params.get('role')
            status_param = request.query_params.get('status')
            search = request.query_params.get('search', '')
            
            users = WebUser.objects.exclude(role=WebUserRole.ROOT)
            
            if role:
                users = users.filter(role=role)
                
            if status_param:
                users = users.filter(status=status_param)
                
            if search:
                users = users.filter(
                    Q(email__icontains=search) |
                    Q(phone__icontains=search)
                )
                
            users = users.order_by('-created_at')
                
            serializer = WebUserSerializer(users, many=True, exclude=['password'])
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("UserView.list exc=%s, params=%s", e, request.query_params)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response 