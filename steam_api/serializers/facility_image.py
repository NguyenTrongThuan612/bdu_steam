from rest_framework import serializers
from steam_api.models.facility_image import FacilityImage
from steam_api.models.facility import Facility
from steam_api.helpers.google_drive_storage import upload_image_to_drive

class FacilityImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilityImage
        fields = "__all__"

class FacilityImageCreateSerializer(serializers.Serializer):
    facility = serializers.PrimaryKeyRelatedField(
        queryset=Facility.objects.filter(deleted_at=None)
    )
    image = serializers.FileField(required=True)
    
    def create(self, validated_data):
        image_file = validated_data.pop('image')
        image_url = upload_image_to_drive(image_file)
        
        facility_image = FacilityImage.objects.create(
            facility=validated_data['facility'],
            image_url=image_url
        )
        return facility_image 