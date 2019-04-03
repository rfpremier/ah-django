from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Articles
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

    def put(self, request, id, *args, **kwargs):
        
        try:
            article = Articles.objects.filter(id=id)
            
            if article[0].author.id != request.user.id:
                data = {'error':
                        'You are not allowed to edit or delete this article'}

                return Response(data, 
                status=status.HTTP_403_FORBIDDEN)
            serializer = self.serializer_class(
                instance=article[0], data=request.data, partial=True
            )
            serializer.is_valid()
            serializer.save()
            return Response({'article': serializer.data}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "error"}, status=status.HTTP_400_BAD_REQUEST)