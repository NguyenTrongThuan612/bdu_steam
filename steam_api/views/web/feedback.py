import logging
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.permissions import IsNotRoot
from steam_api.middlewares.web_authentication import WebUserAuthentication
from steam_api.models.feedback import Feedback
from steam_api.serializers.feedback import FeedbackSerializer


class WebFeedbackView(viewsets.ViewSet):
    """Read-only feedback access for back-office. Replies live in WebFeedbackReplyView."""
    authentication_classes = (WebUserAuthentication,)

    def get_permissions(self):
        # Admin (manager) and teacher can view; ROOT does not.
        return [IsNotRoot()]

    @swagger_auto_schema(
        operation_description="List all parent feedback with replies (back-office)",
        manual_parameters=[
            openapi.Parameter(
                'app_user', openapi.IN_QUERY, description='Filter by parent (AppUser) ID',
                type=openapi.TYPE_INTEGER, required=False,
            ),
        ],
        responses={200: FeedbackSerializer(many=True)},
    )
    def list(self, request):
        try:
            logging.getLogger().info("WebFeedbackView.list params=%s", request.query_params)
            feedbacks = Feedback.objects.filter(deleted_at__isnull=True)

            app_user_id = request.query_params.get('app_user')
            if app_user_id:
                feedbacks = feedbacks.filter(app_user_id=app_user_id)

            feedbacks = feedbacks.select_related('app_user').order_by('-created_at')
            serializer = FeedbackSerializer(feedbacks, many=True)
            return RestResponse(data=serializer.data, status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebFeedbackView.list exc=%s, params=%s", e, request.query_params)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        operation_description="Retrieve one feedback entry with its replies (back-office)",
        responses={200: FeedbackSerializer, 404: 'Not Found'},
    )
    def retrieve(self, request, pk=None):
        try:
            logging.getLogger().info("WebFeedbackView.retrieve pk=%s", pk)
            feedback = Feedback.objects.select_related('app_user').get(
                pk=pk, deleted_at__isnull=True
            )
            return RestResponse(data=FeedbackSerializer(feedback).data, status=status.HTTP_200_OK).response
        except Feedback.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND).response
        except Exception as e:
            logging.getLogger().exception("WebFeedbackView.retrieve exc=%s, pk=%s", e, pk)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response
