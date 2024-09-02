from rest_framework import routers

from django.urls import include, path

from .views import FollowViewSet, SubscribeViewSet, UsersMeViewSet

router = routers.DefaultRouter()
router.register(r"users/subscriptions", FollowViewSet, basename="myfollows")
router.register(
    r"users/(?P<user_id>\d+)/subscribe", SubscribeViewSet, basename="follows"
)
router.register(r"users", UsersMeViewSet, basename="usersme")

urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path("", include(router.urls)),
    path("", include("djoser.urls")),
]
