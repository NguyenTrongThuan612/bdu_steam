from django.db import models
from steam_api.models.facility import Facility

class FacilityImage(models.Model):
    class Meta:
        db_table = "facility_image"
        verbose_name = "Facility Image"
        verbose_name_plural = "Facility Images"
        ordering = ['-created_at']
    
    id = models.AutoField(primary_key=True)
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name='images',
        help_text="The facility this image belongs to"
    )
    image_url = models.URLField(
        max_length=500,
        help_text="URL of the facility image stored in Firebase Storage"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, default=None)
    
    def soft_delete(self):
        from django.utils import timezone
        self.deleted_at = timezone.now()
        self.save()
    
    @classmethod
    def get_active_images(cls):
        return cls.objects.filter(deleted_at=None) 