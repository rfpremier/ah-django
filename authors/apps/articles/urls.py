from django.conf.urls import url
from django.urls import path
from .views import (
    CreateArticleView, SingleArticleView, RatingView, LikeView, TagView,
    FavouritesView, ShareViaEmail, ShareViaFacebookAndTwitter,
    ListAllArticlesView)

urlpatterns = [
    url(r"^articles/?$",
        CreateArticleView.as_view(),
        name="articles"),

    url(r'^articles/all/?$', ListAllArticlesView.as_view(),
        name="all-articles"),

    url(r'^articles/(?P<slug>[-\w]+)/?$',
        SingleArticleView.as_view(),
        name="single-article"),

    path('articles/<int:article_id>/rating/', RatingView.as_view(),
         name="rate-article"),

    url(r'^articles/(?P<slug>[-\w]+)/likes/?$',
        LikeView.as_view(), name="like_article"),
    url(r'^articles/(?P<slug>[-\w]+)/likes/(?P<type>[-\w]+)/?$',
        LikeView.as_view(), name="likes_count"),

    path('tags', TagView.as_view(), name="tags"),

    path('articles/<article_slug>/favorite',
         FavouritesView.as_view(), name="favorite-article"),

    path('favorite/articles',
         FavouritesView.as_view(), name="favorites"),
    path('articles/<slug>/share/email/',
         ShareViaEmail.as_view(), name='email_share'
         ),
    path('articles/<slug>/share/facebook/',
         ShareViaFacebookAndTwitter.as_view(), name='facebook_share'
         ),
    path('articles/<slug>/share/twitter/',
         ShareViaFacebookAndTwitter.as_view(), name='twitter_share'
         )

]
