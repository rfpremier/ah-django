from rest_framework.generics import (CreateAPIView,
                                     ListAPIView, RetrieveUpdateDestroyAPIView)
from rest_framework.response import Response
from rest_framework import status
from .models import Articles, Comments, Rating
from .serializers import (ArticlesSerializer, CommentsSerializer,
                          RatingSerializer)
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from datetime import datetime


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


class RatingView(CreateAPIView, ListAPIView):
    lookup_field = 'article_id'
    permission_classes = (IsAuthenticated,)
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def post(self, request, article_id, *args, **kwargs):
        rating = get_object_or_404(Articles, id=article_id)
        if request.user.is_authenticated:
            rating = request.data.get('rating', {})
            user_id = {"user_id": request.user.id}
            rating.update(user_id)
            article_id = {"article_id": article_id}
            rating.update(article_id)
            serializer = self.serializer_class(
                data=rating
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


class CreateCommentView(CreateAPIView, ListAPIView):
    '''Endpoint for creating a comments'''
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer
    lookup_field = 'article_slug'

    def post(self, request, article_slug):
        '''Handles all post requests to create a comment'''

        if Articles.objects.filter(slug=article_slug).exists():
            # check if user is authorized
            if request.user.is_authenticated:
                comment = request.data.get('comment', {})
                author = request.user.username
                created_at = datetime.now()
                updated_at = datetime.now()

                comment.update({'author': author})
                comment.update({'article_slug': article_slug})
                comment.update({'created_at': created_at})
                comment.update({'updated_at': updated_at})

                serializer = self.serializer_class(data=comment)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"error": "Please login"},
                    status=status.HTTP_403_FORBIDDEN
                )

        else:
            return Response({"error": "Article does not exist"},
                            status=status.HTTP_404_NOT_FOUND)

    def get(self, request, article_slug):
        '''Handles all get requests by users to view the
           comments of a particular article
        '''
        if Articles.objects.filter(slug=article_slug).exists():
            queryset = self.get_queryset().filter(article_slug=article_slug)
            serializer = CommentsSerializer(
                queryset, many=True, context={'request': request})

            count = len(serializer.data)

            if count > 0:
                return Response({"Comments": serializer.data,
                                 "Count": count},
                                status=status.HTTP_200_OK)
            else:
                return Response({"error": "Artcile has no comments"},
                                status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Article does not exist"},
                            status=status.HTTP_404_NOT_FOUND)


class UpdateDeleteCommentView(RetrieveUpdateDestroyAPIView):
    '''Handles all requests for updating and deleting requests'''
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer
    lookup_field = 'id'

    def put(self, request, article_slug, id):
        '''Handles all requests by user to update their comments'''
        if Articles.objects.filter(slug=article_slug).exists():
            if Comments.objects.filter(id=id,
                                       article_slug=article_slug).exists():
                if request.user.is_authenticated:
                    comments = Comments.objects.filter(id=id)

                    if comments[0].author != request.user.username:
                        data = {'error':
                                'You are not allowed to edit this  comment'}

                        return Response(data, status=status.HTTP_403_FORBIDDEN)
                    comm = request.data.get('comment', {})
                    time = Comments.objects.filter(id=id)
                    created = time[0].created_at
                    updated_at = datetime.now()

                    comm.update({'author': request.user.username})
                    comm.update({'article_slug': article_slug})
                    comm.update({'updated_at': updated_at})
                    comm.update({'created_at': created})

                    serializer = self.serializer_class(
                                    instance=comments[0], data=comm,
                                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response({'Comment': serializer.data},
                                    status=status.HTTP_200_OK)

                else:
                    return Response(
                        {"error": "Please login"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            else:
                return Response({"error": "comment does not exist"},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Article does not exist"},
                            status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, article_slug, id):
        '''handles all requests for uses to delete their comments'''
        if Articles.objects.filter(slug=article_slug).exists():
            if Comments.objects.filter(id=id,
                                       article_slug=article_slug).exists():
                if request.user.is_authenticated:
                    comments = Comments.objects.filter(id=id)

                    if comments[0].author == request.user.username:
                        comment = Comments.objects.get(id=id)
                        comment.delete()
                        return Response({"Message": "Comment deleted"},
                                        status=status.HTTP_200_OK)
                    else:
                        return Response({"error":
                                        "You cannot delete this comment"},
                                        status=status.HTTP_403_FORBIDDEN)
                else:
                    return Response(
                        {"error": "Please login"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            else:
                return Response({"error": "comment does not exist"},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Article does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
