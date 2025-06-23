from drf_yasg.utils import swagger_auto_schema
import logging

from rest_framework import viewsets, status
from rest_framework.decorators import action

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.permissions import IsRoot
from steam_api.middlewares.web_authentication import WebUserAuthentication
from steam_api.models.web_user import WebUser, WebUserRole, WebUserStatus
from steam_api.serializers.web_user import CreateWebUserSerializer

class RootView(viewsets.ViewSet):
    authentication_classes = (WebUserAuthentication, )
    permission_classes = (IsRoot, )

    @action(methods=["POST"], detail=False, url_path="users")
    @swagger_auto_schema(request_body=CreateWebUserSerializer)
    def create_user(self, request):
        try:
            logging.getLogger().info("RootView.create_user req=%s", request.data)
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
            logging.getLogger().exception("RootView.create_user exc=%s, req=%s", e, request.data)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response