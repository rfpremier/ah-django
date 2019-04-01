from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import CreateAPIView, ListAPIView
from django.shortcuts import get_object_or_404

from .models import Articles
from ..authentication.models import User
from .serializers import ArticlesSerializer


class ArticleView(CreateAPIView, ListAPIView):
    queryset = Articles.objects.all()

    serializer_class = ArticlesSerializer

    # def perform_create(self, serializer):
    #     author = get_object_or_404(User, username=self.request.data.get('author'))
    #     return serializer.save(author=author)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)