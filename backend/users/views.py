from django.shortcuts import render
from rest_framework import viewsets, mixins, permissions, filters
from .serializers import UserSerializer, AvatarSerializer, FollowSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from .pagination import CustomPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from http import HTTPStatus
from .models import Follow
from django.shortcuts import get_object_or_404
from foodgram_backend.settings import BASE_DIR

User = get_user_model()


class UserAvatarViewSet(APIView):
    serializer_class = AvatarSerializer
    permission_classes = (IsAuthenticated, )

    def put(self, request):
        user = request.user
        serializer = self.serializer_class(user,
                                           data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = '"http://foodgram.example.org' + \
            serializer.data.get('avatar')                   # ОТВЕТ

        return Response({'avatar': response})

    def delete(self, request):
        User.objects.filter(username=request.user).update(avatar=None)
        return Response(status=HTTPStatus.NO_CONTENT)




class FollowViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated, )
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ('=following__username', )
    lookup_value_regex = ''

    def get_queryset(self):
        follows_list = []

        for item in Follow.objects.filter(user_id=self.request.user.id):
            follows_list.append(User.objects.filter(id=item.following_id))
        
        if not follows_list:
            return Follow.objects.none()
        follows_qs = follows_list[0].union(*follows_list[1:])

        return follows_qs


class SubscribeViewSet(APIView):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )

    def post(self, request, id):
        follow = get_object_or_404(User, id=id)
        if Follow.objects.filter(following_id=id, user_id=request.user.id).exists() or (request.user.id == id):
            return Response({'errors': 'Подписка уже существует или невозможна.'}, status=HTTPStatus.BAD_REQUEST)

        serializer = FollowSerializer(follow, context={'request': request})
        Follow.objects.create(following_id=id, user_id=request.user.id)

        return Response(serializer.data, status=HTTPStatus.CREATED)

    def delete(self, request, id):
        get_object_or_404(User, id=id)
        if Follow.objects.filter(following_id=id, user_id=request.user.id).exists():
            Follow.objects.get(
                following_id=id, user_id=request.user.id).delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response({'errors': 'Вы уже не подписаны.'}, status=HTTPStatus.BAD_REQUEST)


class UsersMeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, )
    pagination_class = None

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
