from rest_framework.generics import (CreateAPIView,
                                     ListAPIView, RetrieveUpdateDestroyAPIView)
from rest_framework.response import Response
from rest_framework import status
from .models import Articles
from .serializers import ArticlesSerializer
from django.shortcuts import get_object_or_404


class CreateArticleView(CreateAPIView, ListAPIView):
    queryset = Articles.objects.all()
    serializer_class = ArticlesSerializer

    def post(self, request):
        if request.user.is_authenticated:
            article = request.data.get('article', {})
            serializer = self.serializer_class(
                data=article
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(author=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
    lookup_field = 'slug'
    queryset = Articles.objects.all()
    serializer_class = ArticlesSerializer

    def put(self, request, slug, *args, **kwargs):

        article = get_object_or_404(Articles, slug=slug)
        if article.author.id != request.user.id:
            data = {'error':
                    'You are not allowed to edit this article'}

            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.serializer_class(
            instance=article, data=request.data, partial=True
        )
        serializer.is_valid()
        serializer.save()
        return Response({'article': serializer.data},
                        status=status.HTTP_200_OK)

    def delete(self, request, slug, *args, **kwargs):
        article = get_object_or_404(Articles, slug=slug)
        if article.author.id != request.user.id:
            data = {'error':
                    'You are not allowed to delete this article'}

            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
        return self.destroy(request, *args, **kwargs)
