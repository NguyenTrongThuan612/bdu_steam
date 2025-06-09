from django.db import models

class AppUser(models.Model):
    class Meta:
        db_table = "app_users"
        
    id = models.AutoField(primary_key=True)
    app_user_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    avatar_url = models.CharField(max_length=255)