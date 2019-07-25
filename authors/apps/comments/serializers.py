from rest_framework import serializers
from .models import Comments, Like
from .history import CommentHistory as history
from authors.apps.notifications.middleware import RequestMiddleware
from django.core.exceptions import ObjectDoesNotExist


class CommentsSerializer(serializers.ModelSerializer):
    article = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    highlighted_text = serializers.CharField(
        allow_null=True, allow_blank=True, min_length=4, required=False)
    likesCount = serializers.SerializerMethodField()

    class Meta:
        model = Comments
        fields = [
            'id',
            'created_at',
            'updated_at',
            'body',
            'user',
            'highlighted_text',
            'article',
            'likesCount',

        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        return Comments.objects.create(**validated_data)

    def get_user(self, obj):
        return {"username": obj.user.username,
                "bio": obj.user.bio,
                "image": obj.user.image}

    def get_article(self, obj):
        return obj.article.slug

    def val_highlighted_text(self, text, article):

        if text is not None and text not in article.body:
            msg_d = ["Highlighted text not part of Article ({})".format(
                article.title)]
            msg = {'highlighted_text': msg_d}
            raise serializers.ValidationError(msg)
        else:
            return text
        
    def get_likesCount(self, obj):
        request = RequestMiddleware(
            get_response=None).thread_local.current_request
        likes_queryset = Like.objects.likes().filter(comment=obj.id)
        dislikes_queryset = Like.objects.dislikes().filter(comment=obj.id)
        likesCount = likes_queryset.count()
        dislikesCount = dislikes_queryset.count()
        try:
            like = Likes.objects.get(user=request.user, comment=obj.id)
            userLike = "commentLike" if like.like == 1 else "commentDislike"
        except ObjectDoesNotExist:
            userLike = None
        count = {'likes': likesCount,
                 'dislikes': dislikesCount,
                 'total': likesCount+dislikesCount,
                 'userAction': userLike}
        return count
        


class CommentHistorySerializer(serializers.ModelSerializer):
    comment_history = serializers.SerializerMethodField()
    comment_id = serializers.SerializerMethodField()

    class Meta:
        model = Comments
        fields = ('comment_id', 'comment_history')

    def get_comment_history(self, obj):
        return history().get_comment_updates(obj.comment_history)

    def get_comment_id(self, obj):
        return obj.id


class CommentsLikesSerializer(serializers.ModelSerializer):
    """
    Like dislike comments serializer
    """

    class Meta:
        model = Like
        fields = ('id', 'comment', 'user',
                  'like', 'created_at', 'updated_at')
        read_only_fields = ('id', 'comment', 'user',
                            'created_at', 'updated_at')

    def create(self, validated_data):
        return Like.objects.create(**validated_data)
