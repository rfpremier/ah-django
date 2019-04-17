from rest_framework.generics import (CreateAPIView,
                                     ListAPIView, RetrieveUpdateDestroyAPIView)
from rest_framework.response import Response
from rest_framework import status, pagination
from rest_framework.pagination import PageNumberPagination
from .models import (Articles, Likes, Rating, Favorites)
from .serializers import (
    ArticlesSerializer, LikesSerializer, RatingSerializer,
    FavoritesSerializer, TagsSerializer)
from ..authentication.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from .filters import ArticleFilter
from datetime import datetime
from rest_framework.renderers import JSONRenderer
from django.template.loader import render_to_string
from django.core.mail import send_mail
import re
from django.conf import settings

from asgiref.sync import async_to_sync
from authors.consumers import send_notification


class ArticlesPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'prev': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'articles': data
        })


class CreateArticleView(CreateAPIView, ListAPIView, PageNumberPagination):
    queryset = Articles.objects.get_queryset().order_by('id')
    ordering = ['-id']
    serializer_class = ArticlesSerializer
    pagination_class = ArticlesPagination

    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ArticleFilter

    def post(self, request):
        if request.user.is_authenticated:
            article = request.data.get('article', {})
            serializer = self.serializer_class(
                data=article
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(author=self.request.user)
            msg = "New article from {} named {}".format(self.request.user,
                                                        article['title'])
            notification = {
                'send_to': ['new_article_notification'],
                'message': msg}
            async_to_sync(send_notification)(notification)
            return Response({'article': serializer.data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response(
                {
                    "status": 403,
                    "error": "Please login"
                }, status=status.HTTP_403_FORBIDDEN
            )

    def get(self, request, *args, **kwargs):

        page_size = request.GET.get('page_size')
        if page_size is None:
            page_size = 10

        pagination.PageNumberPagination.page_size = page_size

        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        """
            GET /api/v1/articles/favorites/
        """

        queryset = Articles.objects.get_queryset().order_by('id')
        username = self.request.GET.get('favorited_by')
        if username:
            try:
                user = User.objects.get(username=username)

                favorites = Favorites.objects.filter(
                    user=user.pk).values("article")
                fav_list = list(favorites)
                fav_items = []
                for item in fav_list:
                    fav_items.append(item.get('article'))

                queryset = queryset.filter(id__in=fav_items)

            except User.DoesNotExist:

                return queryset.none()

        return queryset


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


class LikeView(APIView):

    """creating and updating likes
    """
    permission_classes = (IsAuthenticated,)
    queryset = None
    serializer_class = LikesSerializer

    def post(self, request, slug, *args, **kwargs):
        """Like
        Arguments:
            request {[type]} -- [passed by django ]
            slug {[type]} -- [Slug of the article to like]
        """
        actions = {'like': 1, 'dislike': -1}
        data = request.data
        data['user'] = request.user.id

        action = data.get('action', None)
        if not action:
            return Response({'Errors': 'Action not found'},
                            status=status.HTTP_400_BAD_REQUEST)

        article = get_object_or_404(Articles, slug=slug)
        article_id = article.pk

        actiondb = actions.get(action, 0)
        updatefields = {'like': actiondb}
        likeDict = dict(user=request.user,
                        article=article, like=actiondb)

        try:
            like = Likes.objects.get(
                user=request.user, article=article)
            like.like = actiondb
            like.save()
        except Likes.DoesNotExist:
            like = Likes(**likeDict)
            like.save()
        except IntegrityError:
            return Response({'Errors': 'Something went wrong'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        articleS = ArticlesSerializer(instance=article)
        count = self.countLikes(article_id)
        return Response(count, status=status.HTTP_200_OK)

    def get(self, request, slug, type=None, *args, **kwargs):
        article = get_object_or_404(Articles, slug=slug)
        article_id = article.pk

        count = self.countLikes(article_id)
        if type == 'count':

            return Response(count, status=status.HTTP_200_OK)

        l_serialize = LikesSerializer(self.l_queryset, many=True)
        d_serialize = LikesSerializer(self.d_queryset, many=True)
        import json
        likes = json.loads(JSONRenderer().render(l_serialize.data))
        dislikes = json.loads(JSONRenderer().render(d_serialize.data))
        print(dislikes)

        likesDict = {'likes': likes, 'dislikes': dislikes, 'count': count
                     }
        return Response(likesDict, status=status.HTTP_200_OK)

    def delete(self, request, slug, *args, **kwargs):

        article = get_object_or_404(Articles, slug=slug)
        article_id = article.pk
        try:
            like = Likes.objects.get(
                user=request.user, article=article)
            like.delete()
        except Likes.DoesNotExist:
            return Response({'Errors': 'You have not liked this Article'},
                            status=status.HTTP_404_NOT_FOUND)

        count = self.countLikes(article_id)
        return Response(count, status=status.HTTP_200_OK)

    def countLikes(self, article_id):
        self.l_queryset = Likes.objects.likes().filter(article=article_id)
        self.d_queryset = Likes.objects.dislikes().filter(article=article_id)
        likesCount = self.l_queryset.count()
        dislikesCount = self.d_queryset.count()
        count = {'likes': likesCount,
                 'dislikes': dislikesCount,
                 'total': likesCount+dislikesCount}
        return count



class TagView(ListAPIView):
    queryset = Articles.objects.values('tags')
    ordering = ['-id']
    serializer_class = TagsSerializer

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(
            queryset, many=True)
        result = []
        for taglist in serializer.data:
            for tag in taglist["tags"]:
                result.append(tag)
        return Response(data={"tags": set(result)})


class FavouritesView(APIView):
    """
        A user should be able to add an article to their favorites and
        or unfavorite the article
    """
    lookup_field = 'article_slug'
    permission_classes = (IsAuthenticated,)
    queryset = Favorites.objects.all()
    serializer_class = FavoritesSerializer

    def get(self, request, *args, **kwargs):
        """
            GET /api/v1/articles/favorites/
        """
        user = request.user.id
        favorites = Favorites.objects.filter(user=user).all()
        if favorites:
            serializer = FavoritesSerializer(favorites, many=True)
            return Response(
                {
                    "articles": serializer.data
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "status": 404,
                    "error": "No existing article favorite(s)"
                }, status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, article_slug):
        """
            POST /api/v1/articles/<article_slug>/favorite/
        """
        article = get_object_or_404(Articles, slug=article_slug)
        article_id = article.pk

        favorite = Favorites.objects.filter(
            article=article_id, user=request.user.id).exists()
        if favorite:

            return Response(
                {
                    "status": 403,
                    "error": "Article favorite exists"
                }, status=status.HTTP_403_FORBIDDEN
            )
        else:
            favorite_data = {
                'user': request.user.id
            }

            serializer = self.serializer_class(
                data=favorite_data
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(article=article)
            return Response(
                {
                    "article": serializer.data
                },
                status=status.HTTP_201_CREATED)

    def delete(self, request, article_slug):
        """
            DELETE /api/v1/articles/<article_slug>/unfavorite/
        """

        article = get_object_or_404(Articles, slug=article_slug)
        article_id = article.pk

        favorite = Favorites.objects.filter(
            article=article_id, user=request.user.id)
        if favorite:

            favorite.delete()
            return Response(
                {
                    "message": 'Article favorite deleted'
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "status": 404,
                    "error": "Article favorite not found"
                }, status=status.HTTP_404_NOT_FOUND
            )


class ShareViaEmail(CreateAPIView):
    """
        Share Articles via email
    """
    permission_classes = (IsAuthenticated,)
    lookup_field = 'slug'

    def post(self, request, slug):
        """
            POST a request to /api/articles/<slug>/share/email/
            share the article via email
        """
        if Articles.objects.filter(slug=slug).exists():

            email = request.data['email']

            if email is None:
                return Response({
                    'message': 'Please provide an email',
                },
                    status=status.HTTP_400_BAD_REQUEST)
            elif re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email) is None:
                return Response({
                    'message': 'Please enter a valid email'
                }, status=status.HTTP_400_BAD_REQUEST)

            username = request.user.username

            # format the email
            host = request.get_host()
            protocol = request.scheme
            shared_link = protocol + '://' + host + '/api/articles/' + slug
            subject = "Authors Haven"
            article_title = slug
            message = render_to_string(
                'article_share.html', {
                    'username': str(username).capitalize(),
                    'title': article_title,
                    'link': shared_link
                })
            to_email = email
            from_email = settings.FROM_EMAIL

            send_mail(
                subject,
                message,
                from_email, [
                    to_email,
                ],
                html_message=message,
                fail_silently=False)

            message = {
                'message': 'Article shared successfully',
                'shared_link': shared_link
            }
            return Response(message, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Article does not exist"},
                            status=status.HTTP_404_NOT_FOUND)


class ShareViaFacebookAndTwitter(CreateAPIView):
    """
        Share Articles via facebook or twitter
    """
    permission_classes = (IsAuthenticated,)
    lookup_field = 'slug'

    def post(self, request, slug):
        """
            Share Article depending on the POST request either
            /api/articles/<slug>/share/facebook/ or
            /api/articles/<slug>/share/twitter/
        """
        if Articles.objects.filter(slug=slug).exists():

            host = request.get_host()
            protocol = request.scheme
            article_link = protocol + '://' + host + '/api/articles/' + slug

            facebook_url = "https://www.facebook.com/sharer/sharer.php?u="
            twitter_url = "https://twitter.com/intent/tweet?text="
            shared_link = None
            if request.path == '/api/articles/{}/share/facebook/'.format(slug):
                shared_link = facebook_url + article_link

            elif request.path == (
                            '/api/articles/{}/share/twitter/'.format(slug)):
                shared_link = twitter_url + article_link

            message = {
                'message': 'Article shared successfully',
                'shared_link': shared_link
            }
            return Response(message, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Article does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
