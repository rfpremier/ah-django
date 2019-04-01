from rest_framework import serializers

from .models import Articles


class ArticlesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articles
        fields = [
            'id',
            'title',
            'description',
            'body',
            'image_url',
            'author',
            'created_at'
        ]
