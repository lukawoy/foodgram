from django.shortcuts import render
from rest_framework import viewsets, filters
from .models import Tag, Recipe, Favourites, ShoppingList, IngredientsRecipe, Ingredient
from .serializers import TagSerializer, RecipeSerializer, FavoriteSerializer, ShoppingListSerializer, IngredientSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.views import APIView
from http import HTTPStatus
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .filters import RecipeFilter, IngredientFilter
from rest_framework.decorators import action
import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .permissions import AuthorPermission


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
        # Домен!!!
        return Response({'short-link': f'https://foodgram.example.org/s/{short}'})


class FavoriteViewSet(APIView):
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated, )

    def post(self, request, id):
        serializer = self.serializer_class(
            data={'id': id}, context={'request': request, 'id': id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTPStatus.CREATED)

    def delete(self, request, id):
        if not Favourites.objects.filter(user=self.request.user,
                          recipe=get_object_or_404(Recipe, id=id)).exists():
            return Response(status=HTTPStatus.BAD_REQUEST)
        get_object_or_404(Favourites, user=self.request.user,
                          recipe=get_object_or_404(Recipe, id=id)).delete()
        return Response(status=HTTPStatus.NO_CONTENT)

# ПОВТОРЕНИЕ КОДА-----------------------------------------------------


class ShoppingListViewSet(APIView):
    # queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer

    def post(self, request, id):
        serializer = self.serializer_class(
            data={'id': id}, context={'request': request, 'id': id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTPStatus.CREATED)

    def delete(self, request, id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=id)
        if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
            ShoppingList.objects.get(user=user, recipe=recipe).delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response({'errors': 'Такого рецепта нет в списке покупок.'}, status=HTTPStatus.BAD_REQUEST)


class DownloadShoppingListViewSet(APIView):
    def get(self, request):
        shopping_cart = {}

        for recipe in ShoppingList.objects.filter(user=request.user):
            for product in IngredientsRecipe.objects.filter(recipe_id=recipe.recipe_id):
                ingredient = f'{product.ingredient.name} ({product.ingredient.measurement_unit})'
                amount = product.amount

                if shopping_cart.get(ingredient):
                    shopping_cart[ingredient] += amount
                else:
                    shopping_cart[ingredient] = amount

        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="Shopping_cart.csv"'})

        writer = csv.writer(response)
        for item in shopping_cart.keys():
            writer.writerow([f'{str(item)} - {str(shopping_cart[item])}'])

        return response


class GetRecipeShortLink(APIView):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()

    def get(self, request, short_url):
        recipe = get_object_or_404(Recipe, short_url=short_url)
        serializer = RecipeSerializer(recipe, context={'request': request})
        return Response(serializer.data)
