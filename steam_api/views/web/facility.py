import logging
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.web_authentication import WebUserAuthentication
from steam_api.models.facility import Facility
from steam_api.serializers.facility import (
    FacilitySerializer,
    FacilityCreateSerializer,
    FacilityUpdateSerializer
)
from steam_api.middlewares.permissions import IsManager

logger = logging.getLogger(__name__)

class WebFacilityView(viewsets.ViewSet):
    authentication_classes = (WebUserAuthentication,)
    permission_classes = (IsManager,)
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        operation_description="Create a new facility",
        request_body=FacilityCreateSerializer,
        responses={
            201: FacilitySerializer,
            400: "Bad Request",
            500: "Internal Server Error"
        }
    )
    def create(self, request: Request) -> Response:
        try:
            logger.info("WebFacilityView.create req=%s", request.data)
            
            serializer = FacilityCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return RestResponse(
                    data=serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Vui lòng kiểm tra lại dữ liệu!"
                ).response
            
            facility = serializer.save()
            
            return RestResponse(
                data=FacilitySerializer(facility).data,
                status=status.HTTP_201_CREATED
            ).response
            
        except Exception as e:
            logger.exception("WebFacilityView.create exc=%s, req=%s", e, request.data)
            return RestResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).response

    @swagger_auto_schema(
        operation_description="Get list of facilities",
        responses={
            200: FacilitySerializer(many=True),
            500: "Internal Server Error"
        }
    )
    def list(self, request: Request) -> Response:
        try:
            queryset = Facility.get_active_facilities().order_by('-created_at')
            data = FacilitySerializer(queryset, many=True).data

            return RestResponse(
                data=data,
                status=status.HTTP_200_OK
            ).response
            
        except Exception as e:
            logger.exception("WebFacilityView.list exc=%s", e)
            return RestResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Internal server error"
            ).response


    @swagger_auto_schema(
        operation_description="Update facility by ID",
        request_body=FacilityUpdateSerializer,
        responses={
            200: FacilitySerializer,
            400: "Bad Request",
            404: "Not Found",
            500: "Internal Server Error"
        }
    )
    def update(self, request: Request, pk: int) -> Response:
        try:
            try:
                facility = Facility.objects.get(id=pk, deleted_at=None)
            except Facility.DoesNotExist:
                return RestResponse(
                    status=status.HTTP_404_NOT_FOUND,
                    message="Không tìm thấy cơ sở vật chất này!"
                ).response
            
            serializer = FacilityUpdateSerializer(facility, data=request.data, partial=True)
            if not serializer.is_valid():
                return RestResponse(
                    data=serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Vui lòng kiểm tra lại dữ liệu!"
                ).response
            
            updated_facility = serializer.save()
            
            return RestResponse(
                data=FacilitySerializer(updated_facility).data,
                status=status.HTTP_200_OK
            ).response
            
        except Exception as e:
            logger.exception("WebFacilityView.update exc=%s, pk=%s, req=%s", e, pk, request.data)
            return RestResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).response

    @swagger_auto_schema(
        operation_description="Delete facility by ID",
        responses={
            204: "No Content",
            404: "Not Found",
            500: "Internal Server Error"
        }
    )
    def destroy(self, request: Request, pk: int) -> Response:
        try:
            try:
                facility = Facility.objects.get(id=pk, deleted_at=None)
            except Facility.DoesNotExist:
                return RestResponse(
                    status=status.HTTP_404_NOT_FOUND,
                    message="Không tìm thấy cơ sở vật chất này!"
                ).response
            
            facility.soft_delete()
            
            return RestResponse(status=status.HTTP_204_NO_CONTENT).response
            
        except Exception as e:
            logger.exception("WebFacilityView.destroy exc=%s, pk=%s", e, pk)
            return RestResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).response