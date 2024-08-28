from rest_framework import routers

from django.urls import include, path

from .views import (
    DownloadShoppingListViewSet, FavoriteViewSet,
    IngredientViewSet, RecipeViewSet, ShoppingListViewSet,
    TagViewSet
)

router = routers.DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'recipes/(?P<recipe_id>\d+)/favorite',
                FavoriteViewSet, basename='favorite')
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
                ShoppingListViewSet, basename='shopping_cart')

urlpatterns = [
    path('recipes/download_shopping_cart/',
         DownloadShoppingListViewSet.as_view()),
    path('', include(router.urls)),
]
