from rest_framework import serializers

class CreateAppSessionSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)