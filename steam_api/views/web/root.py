from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import logging

from rest_framework import viewsets, status
from rest_framework.decorators import action

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.permissions import IsRoot
from steam_api.middlewares.web_authentication import WebUserAuthentication
from steam_api.models.web_user import WebUser, WebUserRole, WebUserStatus
from steam_api.serializers.web_user import CreateWebUserSerializer, UpdateWebUserSerializer, WebUserSerializer

class RootView(viewsets.ViewSet):
    authentication_classes = (WebUserAuthentication, )
    permission_classes = (IsRoot, )

    @swagger_auto_schema(request_body=CreateWebUserSerializer)
    def create(self, request):
        try:
            logging.getLogger().info("RootView.create req=%s", request.data)
            validate = CreateWebUserSerializer(data=request.data)

            if not validate.is_valid():
                return RestResponse(validate.errors, status=status.HTTP_400_BAD_REQUEST, message="Vui lòng kiểm tra lại dữ liệu của bạn!").response
            
            validated_data = validate.validated_data
            
            if WebUser.objects.filter(email=validated_data["email"]).exists():
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, message="Email đã được sử dụng bởi một tài khoản khác!").response
            
            _password: str = validated_data.pop("password")

            user = WebUser(**validated_data)
            user.set_password(_password)
            user.status = WebUserStatus.UNVERIFIED
            user.save() 
                
            if user.id is None:
                return RestResponse(message="Failed to create user.", status=status.HTTP_500_INTERNAL_SERVER_ERROR).response
            # audit_back_office(request.user, "Tạo tài khoản", user.email)
            return RestResponse(message="Thành công!", status=status.HTTP_201_CREATED).response
        except Exception as e:
            logging.getLogger().exception("RootView.create exc=%s, req=%s", e, request.data)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        request_body=UpdateWebUserSerializer,
        responses={
            200: WebUserSerializer(),
            400: 'Bad Request',
            404: 'Not Found',
            500: 'Internal Server Error'
        }
    )
    def update(self, request, pk=None):
        try:
            logging.getLogger().info("RootView.update pk=%s, req=%s", pk, request.data)
            
            try:
                user = WebUser.objects.get(pk=pk)
            except WebUser.DoesNotExist:
                return RestResponse(
                    status=status.HTTP_404_NOT_FOUND,
                    message="Không tìm thấy người dùng!"
                ).response
            
            serializer = UpdateWebUserSerializer(
                instance=user,
                data=request.data,
                context={'request': request}
            )
            
            if not serializer.is_valid():
                return RestResponse(
                    data=serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Vui lòng kiểm tra lại dữ liệu!"
                ).response
            
            updated_user = serializer.save()
            response_serializer = WebUserSerializer(updated_user, exclude=['password'])
            
            return RestResponse(
                data=response_serializer.data,
                status=status.HTTP_200_OK,
                message="Cập nhật thông tin thành công!"
            ).response
            
        except Exception as e:
            logging.getLogger().exception("RootView.update exc=%s, pk=%s, req=%s", e, pk, request.data)
            return RestResponse(
                data={"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ).response