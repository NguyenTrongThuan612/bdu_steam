import logging
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.app_authentication import AppAuthentication
from steam_api.models.feedback import Feedback
from steam_api.serializers.feedback import CreateFeedbackSerializer, CreatedFeedbackSerializer


class AppFeedbackView(viewsets.ViewSet):
    authentication_classes = (AppAuthentication,)

    @swagger_auto_schema(
        operation_description="Submit feedback as a parent",
        request_body=CreateFeedbackSerializer,
        responses={201: CreatedFeedbackSerializer, 400: 'Bad Request'},
    )
    def create(self, request):
        try:
            logging.getLogger().info("AppFeedbackView.create req=%s", request.data)
            serializer = CreateFeedbackSerializer(data=request.data)
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response

            feedback = Feedback.objects.create(
                app_user=request.user, **serializer.validated_data
            )
            return RestResponse(
                data=CreatedFeedbackSerializer(feedback).data, status=status.HTTP_201_CREATED
            ).response
        except Exception as e:
            logging.getLogger().exception("AppFeedbackView.create exc=%s, req=%s", e, request.data)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response
