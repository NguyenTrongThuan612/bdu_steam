from rest_framework import serializers

from steam_api.models.feedback import Feedback
from steam_api.models.feedback_reply import FeedbackReply
from steam_api.serializers.app_user import AppUserSerializer


class ReplyAuthorSerializer(serializers.Serializer):
    """Safe WebUser fields only.

    WebUser extends AbstractBaseUser, so a full ModelSerializer would leak the
    password hash. Expose just the identity fields.
    """
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    role = serializers.CharField(read_only=True)


class FeedbackReplySerializer(serializers.ModelSerializer):
    web_user = ReplyAuthorSerializer(read_only=True)

    class Meta:
        model = FeedbackReply
        fields = "__all__"


class FeedbackSerializer(serializers.ModelSerializer):
    app_user = AppUserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    def get_replies(self, obj):
        replies = obj.replies.filter(deleted_at__isnull=True).order_by('created_at')
        return FeedbackReplySerializer(replies, many=True).data

    class Meta:
        model = Feedback
        fields = "__all__"


class CreateFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["content"]

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Nội dung phản ánh không được để trống.")
        return value


class CreatedFeedbackSerializer(serializers.ModelSerializer):
    """Parent-facing create response.

    Deliberately excludes `replies`/`web_user` so the mobile surface is never
    coupled to staff identity (email/role). Keep FeedbackSerializer for back-office.
    """
    class Meta:
        model = Feedback
        fields = ["id", "content", "created_at"]


class CreateFeedbackReplySerializer(serializers.ModelSerializer):
    feedback = serializers.PrimaryKeyRelatedField(
        queryset=Feedback.objects.filter(deleted_at__isnull=True)
    )

    class Meta:
        model = FeedbackReply
        fields = ["feedback", "content"]

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Nội dung phản hồi không được để trống.")
        return value


class UpdateFeedbackReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackReply
        fields = ["content"]

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Nội dung phản hồi không được để trống.")
        return value
