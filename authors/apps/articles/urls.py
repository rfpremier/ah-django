from django.conf.urls import url
from django.urls import path

from .views import (
    CreateArticleView, SingleArticleView
)

urlpatterns = [
    url(r"^articles/?$",
        CreateArticleView.as_view(),
        name="articles"),

    url(r'^articles/(?P<slug>[-\w]+)/?$',
        SingleArticleView.as_view(),
        name="single-article")
]
