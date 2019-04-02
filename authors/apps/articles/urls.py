from django.conf.urls import url
from django.urls import path
from .views import (
<<<<<<< 00b800a238ca584be790682e553453ec5982f183
    CreateArticleView, SingleArticleView, RatingView, LikeView
=======
    CreateArticleView, SingleArticleView, RatingView
)

from .views import (
    CreateArticleView, SingleArticleView
>>>>>>> * 164857218-feature(article):
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
<<<<<<< 00b800a238ca584be790682e553453ec5982f183
    url(r'^articles/(?P<slug>[-\w]+)/likes/?$',
        LikeView.as_view(), name="like_article"),
    url(r'^articles/(?P<slug>[-\w]+)/likes/(?P<type>[-\w]+)/?$',
        LikeView.as_view(), name="likes_count"),
=======


>>>>>>> * 164857218-feature(article):
]
