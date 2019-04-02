from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Articles
from ..authentication.models import User
from .serializers import ArticlesSerializer


class CreateArticleView(CreateAPIView, ListAPIView):
    queryset = Articles.objects.all()
    serializer_class = ArticlesSerializer

    def post(self, request):
        if request.user.is_authenticated:
            article = request.data.get('article', {})
            author = {"author": request.user.id}
            article.update(author)
            serializer = self.serializer_class(
                data=article
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {
                    "status": 403,
                    "error": "Please login"
                }, status=status.HTTP_403_FORBIDDEN
            )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class SingleArticleView(RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    queryset = Articles.objects.all()
    serializer_class = ArticlesSerializer

