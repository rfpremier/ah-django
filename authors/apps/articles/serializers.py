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
        read_only_fields = ["id", "author", "created_at"]

    def create(self, validated_data):
        return Articles.objects.create(**validated_data)
