from rest_framework import serializers

from steam_api.models.app_user import AppUser

class CreateAppSessionSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)

class AppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = '__all__'