import logging
from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.app_authentication import AppAuthentication
from steam_api.models.facility import Facility
from steam_api.serializers.facility import FacilitySerializer

logger = logging.getLogger(__name__)


class AppFacilityView(viewsets.ViewSet):
    authentication_classes = (AppAuthentication, )
    
    @swagger_auto_schema(
        operation_description="Get list of facilities for app",
        responses={
            200: FacilitySerializer(many=True),
            500: "Internal Server Error"
        }
    )
    def list(self, request: Request) -> Response:
        try:
            queryset = Facility.get_active_facilities().order_by('-created_at')
            data = FacilitySerializer(queryset, many=True, context={'request': request}).data

            return RestResponse(
                data=data,
                status=status.HTTP_200_OK
            ).response
            
        except Exception as e:
            logger.exception("AppFacilityView.list exc=%s", e)
            return RestResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).response