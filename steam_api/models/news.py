from django.db import models
from django.conf import settings

class News(models.Model):
    class Meta:
        db_table = "news"
        
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=1000)
    link = models.URLField()
    image = models.URLField()
    posted_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)