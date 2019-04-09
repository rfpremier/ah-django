from django.conf.urls import url
from django.urls import path
from .views import (
    CreateArticleView, SingleArticleView, RatingView, LikeView,
    CreateCommentView, UpdateDeleteCommentView, TagView
)

urlpatterns = [
    url(r"^articles/?$",
        CreateArticleView.as_view(),
        name="articles"),
    url(r'^articles/(?P<slug>[-\w]+)/?$',
        SingleArticleView.as_view(),
        name="single-article"),
    path('articles/<int:article_id>/rating/', RatingView.as_view(),
         name="rate-article"),
    url(r'^articles/(?P<slug>[-\w]+)/likes/?$',
        LikeView.as_view(), name="like_article"),
    url(r'^articles/(?P<slug>[-\w]+)/likes/(?P<type>[-\w]+)/?$',
        LikeView.as_view(), name="likes_count"),

    url(r'^articles/(?P<article_slug>[-\w]+)/comments/?$',
        CreateCommentView.as_view(),
        name="create-get-comment"),

    path('articles/<article_slug>/comments/<int:id>',
         UpdateDeleteCommentView.as_view(),
         name="update-delete-comment"),
    path('tags', TagView.as_view(), name="tags")
]
