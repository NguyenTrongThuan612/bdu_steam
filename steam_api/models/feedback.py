from django.db import models

from steam_api.models.app_user import AppUser


class Feedback(models.Model):
    class Meta:
        db_table = "feedbacks"

    id = models.BigAutoField(primary_key=True)
    app_user = models.ForeignKey(
        AppUser, on_delete=models.CASCADE, related_name="feedbacks"
    )
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"Feedback#{self.id} - app_user={self.app_user_id}"
