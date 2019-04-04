from django.conf.urls import url
from django.urls import path
from .views import (
    CreateArticleView, SingleArticleView, RatingView,
    CreateCommentView, UpdateDeleteCommentView
)

urlpatterns = [
    url(r"^articles/?$",
        CreateArticleView.as_view(),
        name="articles"),

    url(r'^articles/(?P<slug>[-\w]+)/?$',
        SingleArticleView.as_view(),
        name="single-article"),
    url(r"^articles/$", CreateArticleView.as_view(), name="articles"),
    path('articles/<int:article_id>/rating/', RatingView.as_view(),
         name="rate-article"),

    url(r'^articles/(?P<article_slug>[-\w]+)/comments/?$',
        CreateCommentView.as_view(),
        name="create-get-comment"),

    path('articles/<article_slug>/comments/<int:id>',
         UpdateDeleteCommentView.as_view(),
         name="update-delete-comment")
]
