from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import logging
import random
import string
import threading

from rest_framework import viewsets, status
from rest_framework.decorators import action

from steam_api.helpers.response import RestResponse
from steam_api.helpers.send_html_email import send_html_template_email
from steam_api.middlewares.permissions import IsRoot
from steam_api.middlewares.web_authentication import WebUserAuthentication
from steam_api.models.web_user import WebUser, WebUserRole, WebUserStatus
from steam_api.serializers.web_user import CreateWebUserSerializer, UpdateWebUserSerializer, WebUserSerializer

class RootView(viewsets.ViewSet):
    authentication_classes = (WebUserAuthentication, )
    permission_classes = (IsRoot, )

    def __generate_random_password(self, length=12):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))

    def __send_password_reset_email(self, user, new_password):
        def send_mail():
            try:
                send_html_template_email(
                    to=[user.email],
                    subject="[Trường Đại học Bình Dương] Thông báo đặt lại mật khẩu",
                    template_name="password_reset.html",
                    context={
                        "user_name": user.name,
                        "new_password": new_password
                    }
                )
            except Exception as e:
                logging.getLogger().exception("RootView.__send_password_reset_email exc=%s", e)

        thread = threading.Thread(target=send_mail)
        thread.daemon = True
        thread.start()

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

    @swagger_auto_schema(
        responses={
            200: 'Success',
            404: 'User not found',
            500: 'Internal Server Error'
        }
    )
    @action(detail=True, methods=['post'], url_path='reset-password')
    def reset_password(self, request, pk=None):
        try:
            logging.getLogger().info("RootView.reset_password pk=%s", pk)
            
            try:
                user = WebUser.objects.get(pk=pk)
            except WebUser.DoesNotExist:
                return RestResponse(
                    status=status.HTTP_404_NOT_FOUND,
                    message="Không tìm thấy người dùng!"
                ).response

            new_password = self.__generate_random_password()
            user.set_password(new_password)
            user.save(update_fields=['password'])
            
            self.__send_password_reset_email(user, new_password)
            
            return RestResponse(
                status=status.HTTP_200_OK,
                message="Mật khẩu đã được đặt lại và gửi đến email của người dùng!"
            ).response
            
        except Exception as e:
            logging.getLogger().exception("RootView.reset_password exc=%s, pk=%s", e, pk)
            return RestResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Lỗi khi đặt lại mật khẩu!"
            ).response