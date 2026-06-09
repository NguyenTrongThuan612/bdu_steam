import logging
from django.utils import timezone
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema

from steam_api.helpers.response import RestResponse
from steam_api.middlewares.permissions import IsNotRoot
from steam_api.middlewares.web_authentication import WebUserAuthentication
from steam_api.models.feedback_reply import FeedbackReply
from steam_api.serializers.feedback import (
    FeedbackReplySerializer,
    CreateFeedbackReplySerializer,
    UpdateFeedbackReplySerializer,
)


class WebFeedbackReplyView(viewsets.ViewSet):
    """Back-office replies to parent feedback. Admin (manager) and teacher only; ROOT excluded."""
    authentication_classes = (WebUserAuthentication,)

    def get_permissions(self):
        return [IsNotRoot()]

    @swagger_auto_schema(
        operation_description="Reply to a feedback entry (admin/teacher)",
        request_body=CreateFeedbackReplySerializer,
        responses={201: FeedbackReplySerializer, 400: 'Bad Request'},
    )
    def create(self, request):
        try:
            logging.getLogger().info("WebFeedbackReplyView.create req=%s", request.data)
            serializer = CreateFeedbackReplySerializer(data=request.data)
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response

            reply = FeedbackReply.objects.create(
                feedback=serializer.validated_data['feedback'],
                web_user=request.user,
                content=serializer.validated_data['content'],
            )
            return RestResponse(
                data=FeedbackReplySerializer(reply).data, status=status.HTTP_201_CREATED
            ).response
        except Exception as e:
            logging.getLogger().exception("WebFeedbackReplyView.create exc=%s, req=%s", e, request.data)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        operation_description="Edit a reply's content (admin/teacher)",
        request_body=UpdateFeedbackReplySerializer,
        responses={200: FeedbackReplySerializer, 400: 'Bad Request', 404: 'Not Found'},
    )
    def update(self, request, pk=None):
        try:
            logging.getLogger().info("WebFeedbackReplyView.update pk=%s, req=%s", pk, request.data)
            serializer = UpdateFeedbackReplySerializer(data=request.data)
            if not serializer.is_valid():
                return RestResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST).response

            try:
                reply = FeedbackReply.objects.get(pk=pk, deleted_at__isnull=True)
            except FeedbackReply.DoesNotExist:
                return RestResponse(status=status.HTTP_404_NOT_FOUND).response

            reply.content = serializer.validated_data['content']
            reply.save(update_fields=['content', 'updated_at'])
            return RestResponse(
                data=FeedbackReplySerializer(reply).data, status=status.HTTP_200_OK
            ).response
        except Exception as e:
            logging.getLogger().exception("WebFeedbackReplyView.update exc=%s, pk=%s, req=%s", e, pk, request.data)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        operation_description="Soft-delete a reply (admin/teacher)",
        responses={200: 'OK', 404: 'Not Found'},
    )
    def destroy(self, request, pk=None):
        try:
            logging.getLogger().info("WebFeedbackReplyView.destroy pk=%s", pk)
            try:
                reply = FeedbackReply.objects.get(pk=pk, deleted_at__isnull=True)
            except FeedbackReply.DoesNotExist:
                return RestResponse(status=status.HTTP_404_NOT_FOUND).response

            reply.deleted_at = timezone.now()
            reply.save(update_fields=['deleted_at'])
            return RestResponse(status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("WebFeedbackReplyView.destroy exc=%s, pk=%s", e, pk)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response
