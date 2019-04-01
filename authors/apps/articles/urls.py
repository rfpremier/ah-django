from django.conf.urls import url

from .views import (
    ArticleView,
)

urlpatterns = [
    url(r"^articles/$", ArticleView.as_view(), name="articles"),

]
