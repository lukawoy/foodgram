from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework import routers

from .views import TagViewSet, RecipeViewSet, FavoriteViewSet, ShoppingListViewSet, GetRecipeShortLink, IngredientViewSet

router = routers.DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('recipes/shopping_cart/', ShoppingListViewSet.as_view()),
    path('recipes/<int:id>/shopping_cart/', ShoppingListViewSet.as_view()),
    path('recipes/<int:id>/favorite/', FavoriteViewSet.as_view()),
    path('', include(router.urls)),
]
