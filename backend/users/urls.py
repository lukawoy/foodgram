from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework import routers

from .views import UserAvatarViewSet, FollowViewSet, SubscribeViewSet, UsersMeViewSet

router = routers.DefaultRouter()

router.register(r'users/subscriptions', FollowViewSet, basename='follows')
router.register(r'users/me', UsersMeViewSet, basename='usersme')

urlpatterns = [
    path('users/<int:id>/subscribe/', SubscribeViewSet.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/avatar/', UserAvatarViewSet.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls'))
]
