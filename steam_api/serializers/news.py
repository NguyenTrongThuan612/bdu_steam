from rest_framework import serializers
from steam_api.models.news import News

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = "__all__"


class CreateNewsSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)
    link = serializers.URLField(required=True)
    image = serializers.FileField(required=True)
    posted_at = serializers.DateTimeField(required=True)

class UpdateNewsSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    link = serializers.URLField(required=False)
    image = serializers.FileField(required=False)
    posted_at = serializers.DateTimeField(required=False)