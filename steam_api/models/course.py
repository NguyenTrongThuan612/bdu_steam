from django.db import models
from django.conf import settings

class Course(models.Model):
    class Meta:
        db_table = "courses"
        
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    thumbnail_url = models.CharField(max_length=500, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration = models.IntegerField(help_text="Duration in minutes", default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def get_thumbnail_url(self):
        return f"{settings.APP_DOMAIN}{self.thumbnail_url}"