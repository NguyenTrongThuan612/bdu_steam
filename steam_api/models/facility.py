from django.db import models


class Facility(models.Model):
    class Meta:
        db_table = "facility"
        verbose_name = "Facility"
        verbose_name_plural = "Facilities"
        ordering = ['-created_at']
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, help_text="Name of the facility")
    description = models.TextField(help_text="Description of the facility")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, default=None)
    
    def soft_delete(self):
        from django.utils import timezone
        self.deleted_at = timezone.now()
        self.save()
    
    @classmethod
    def get_active_facilities(cls):
        return cls.objects.filter(deleted_at=None) 