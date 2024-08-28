import csv
import os
from http import HTTPStatus

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from dotenv import load_dotenv
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import IngredientFilter, RecipeFilter
from .models import (Favourites, Ingredient, IngredientsRecipe, Recipe,
                     ShoppingList, Tag)
from .permissions import AuthorPermission
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingListSerializer,
                          TagSerializer)

load_dotenv(override=True)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-pub_date')
    serializer_class = RecipeSerializer
    permission_classes = (AuthorPermission, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    @action(detail=True, methods=['GET'], url_path='get-link')
    def get_link(self, request, pk=None):
        short = get_object_or_404(Recipe, id=pk).short_url
        return Response(
            {'short-link': f'https://{os.getenv("DOMAIN")}/s/{short}'}
        )


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated, )
    http_method_names = ['delete', 'post']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, recipe=get_object_or_404(
            Recipe, id=self.kwargs.get('recipe_id')))

    def delete(self, request, recipe_id):
        if not Favourites.objects.filter(user=self.request.user,
                                         recipe=get_object_or_404(
                                             Recipe, id=recipe_id)).exists():
            return Response(status=HTTPStatus.BAD_REQUEST)
        get_object_or_404(Favourites, user=self.request.user,
                          recipe=get_object_or_404(Recipe,
                                                   id=recipe_id)).delete()
        return Response(status=HTTPStatus.NO_CONTENT)


class ShoppingListViewSet(FavoriteViewSet):
    serializer_class = ShoppingListSerializer

    def delete(self, request, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
            ShoppingList.objects.get(user=user, recipe=recipe).delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(
            {'errors': 'Такого рецепта нет в списке покупок.'},
            status=HTTPStatus.BAD_REQUEST
        )


class DownloadShoppingListViewSet(APIView):
    def get(self, request):
        shopping_cart = {}

        for recipe in ShoppingList.objects.filter(user=request.user):
            for product in IngredientsRecipe.objects.filter(
                recipe_id=recipe.recipe_id
            ):
                ingredient = f'{product.ingredient.name} '
                f'({product.ingredient.measurement_unit})'
                amount = product.amount

                if shopping_cart.get(ingredient):
                    shopping_cart[ingredient] += amount
                else:
                    shopping_cart[ingredient] = amount

        response = HttpResponse(
            content_type="text/csv",
            headers={
                "Content-Disposition": 'attachment; '
                'filename="Shopping_cart.csv"'
            },
            charset='cp1251')

        writer = csv.writer(response)
        writer.writerow(['Список покупок:'])
        for item in shopping_cart.keys():
            writer.writerow([f'{str(item)} - {str(shopping_cart[item])}'])

        return response


class GetRecipeShortLink(APIView):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (AllowAny,)

    def get(self, request, short_url):
        recipe = get_object_or_404(Recipe, short_url=short_url)
        serializer = RecipeSerializer(recipe, context={'request': request})
        return Response(serializer.data)
