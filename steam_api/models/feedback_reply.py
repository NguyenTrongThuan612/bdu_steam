from django.db import models

from steam_api.models.feedback import Feedback
from steam_api.models.web_user import WebUser


class FeedbackReply(models.Model):
    class Meta:
        db_table = "feedback_replies"

    id = models.BigAutoField(primary_key=True)
    feedback = models.ForeignKey(
        Feedback, on_delete=models.CASCADE, related_name="replies"
    )
    web_user = models.ForeignKey(
        WebUser,
        null=True,
        on_delete=models.SET_NULL,
        related_name="feedback_replies",
    )
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"FeedbackReply#{self.id} - feedback={self.feedback_id}"
