import logging
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.web_authentication import WebUserAuthentication
from steam_api.models.facility_image import FacilityImage
from steam_api.serializers.facility_image import (
    FacilityImageSerializer,
    FacilityImageCreateSerializer
)

logger = logging.getLogger(__name__)


class WebFacilityImageView(viewsets.ViewSet):
    authentication_classes = (WebUserAuthentication,)
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        operation_description="Create a new facility image",
        request_body=FacilityImageCreateSerializer,
        responses={
            201: FacilityImageSerializer,
            400: "Bad Request",
            500: "Internal Server Error"
        }
    )
    def create(self, request: Request) -> Response:
        try:
            logger.info("WebFacilityImageView.create req=%s", request.data)
            
            serializer = FacilityImageCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return RestResponse(
                    data=serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Please check your data!"
                ).response
            
            facility_image = serializer.save()
            
            return RestResponse(
                data=FacilityImageSerializer(facility_image).data,
                status=status.HTTP_201_CREATED
            ).response
            
        except Exception as e:
            logger.exception("WebFacilityImageView.create exc=%s, req=%s", e, request.data)
            return RestResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Internal server error"
            ).response

    @swagger_auto_schema(
        operation_description="Delete facility image by ID",
        responses={
            204: "No Content",
            404: "Not Found",
            500: "Internal Server Error"
        }
    )
    def destroy(self, request: Request, pk: int) -> Response:
        try:
            try:
                facility_image = FacilityImage.objects.get(id=pk, deleted_at=None)
            except FacilityImage.DoesNotExist:
                return RestResponse(
                    status=status.HTTP_404_NOT_FOUND,
                    message="Facility image not found"
                ).response
            
            facility_image.soft_delete()
            
            return RestResponse(status=status.HTTP_204_NO_CONTENT).response
            
        except Exception as e:
            logger.exception("WebFacilityImageView.destroy exc=%s, pk=%s", e, pk)
            return RestResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Internal server error"
            ).response

    @swagger_auto_schema(
        operation_description="Get facility image details by ID",
        responses={
            200: FacilityImageSerializer,
            404: "Not Found",
            500: "Internal Server Error"
        }
    )
    def retrieve(self, request: Request, pk: int) -> Response:
        try:
            try:
                facility_image = FacilityImage.objects.get(id=pk, deleted_at=None)
            except FacilityImage.DoesNotExist:
                return RestResponse(
                    status=status.HTTP_404_NOT_FOUND,
                    message="Facility image not found"
                ).response
            
            return RestResponse(
                data=FacilityImageSerializer(facility_image).data,
                status=status.HTTP_200_OK
            ).response
            
        except Exception as e:
            logger.exception("WebFacilityImageView.retrieve exc=%s, pk=%s", e, pk)
            return RestResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Internal server error"
            ).response 