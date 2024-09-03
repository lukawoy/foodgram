import os
from http import HTTPStatus

from dotenv import load_dotenv

from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet

from .pagination import CustomPagination
from .serializers import AvatarSerializer, FollowSerializer, UserSerializer

load_dotenv(override=True)

User = get_user_model()


class FollowViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("=following__username",)

    def get_queryset(self):
        return User.objects.filter(followings__user=self.request.user)


class SubscribeViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ["post", "delete"]

    def perform_create(self, serializer):
        serializer.save()

    def delete(self, request, user_id):
        following_user = get_object_or_404(User, id=user_id)
        follow = following_user.followings.filter(user_id=request.user.id)
        print(follow)
        if follow.exists():
            follow.delete()
            return Response(status=HTTPStatus.NO_CONTENT)

        return Response(
            {"errors": "Вы уже не подписаны."}, status=HTTPStatus.BAD_REQUEST
        )


class UsersMeViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    @action(
        detail=False,
        methods=["put", "delete"],
        serializer_class=AvatarSerializer,
        permission_classes=(IsAuthenticated,),
        url_path="me/avatar",
    )
    def avatar(self, request):
        if request.method == "PUT":
            serializer = self.serializer_class(request.user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = (
                f'https://{os.getenv("DOMAIN")}'
                f'{serializer.data.get("avatar")}'
            )
            return Response({"avatar": response})

        User.objects.filter(username=request.user).update(avatar=None)
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(["get"], detail=False, permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            request.user, context={"request": request}
        )
        return Response(serializer.data)
