from django.contrib import admin
from django.urls import include, path

from recipes.views import GetRecipeShortLink

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("recipes.urls")),
    path("api/", include("users.urls")),
    path("s/<slug:short_url>/", GetRecipeShortLink.as_view()),
]
