import csv
import os
from http import HTTPStatus

from dotenv import load_dotenv

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .filters import IngredientFilter, RecipeFilter
from .models import Favourites, Ingredient, IngredientsRecipe, Recipe, Tag
from .permissions import AuthorPermission
from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingListSerializer,
    TagSerializer
)
from django.db.models import Sum

load_dotenv(override=True)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by("-pub_date")
    serializer_class = RecipeSerializer
    permission_classes = (AuthorPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(detail=True, methods=["GET"], url_path="get-link")
    def get_link(self, request, pk=None):
        short = get_object_or_404(Recipe, id=pk).short_url
        return Response(
            {"short-link": f'https://{os.getenv("DOMAIN")}/s/{short}'}
        )


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ["delete", "post"]

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            recipe=get_object_or_404(Recipe, id=self.kwargs.get("recipe_id")),
        )

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if not recipe.favorites_recipe.filter(
                user__id=request.user.id).exists():
            return Response(status=HTTPStatus.BAD_REQUEST)

        get_object_or_404(
            Favourites,
            user=self.request.user,
            recipe=get_object_or_404(Recipe, id=recipe_id),
        ).delete()
        return Response(status=HTTPStatus.NO_CONTENT)


class ShoppingListViewSet(FavoriteViewSet):
    serializer_class = ShoppingListSerializer

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        shop_list = recipe.shoppinglist_recipe.filter(user__id=request.user.id)

        if shop_list.exists():
            shop_list.delete()
            return Response(status=HTTPStatus.NO_CONTENT)

        return Response(
            {"errors": "Такого рецепта нет в списке покупок."},
            status=HTTPStatus.BAD_REQUEST,
        )


class DownloadShoppingListViewSet(APIView):
    def get(self, request):
        ingredients = (
            IngredientsRecipe.objects.filter(
                recipe__shoppinglist_recipe__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_amount=Sum("amount"))
            .order_by("ingredient__name")
        )

        response = HttpResponse(
            content_type="text/csv",
            headers={
                "Content-Disposition": "attachment; "
                'filename="Shopping_cart.csv"'
            },
            charset="cp1251",
        )

        writer = csv.writer(response)
        writer.writerow(["Список покупок:"])

        for ingredient in ingredients:
            ingredient_name = ingredient["ingredient__name"]
            amount = ingredient["total_amount"]
            measurement_unit = ingredient["ingredient__measurement_unit"]
            writer.writerow(
                [f"{ingredient_name} - {amount} ({measurement_unit})"]
            )

        return response


class GetRecipeShortLink(APIView):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (AllowAny,)

    def get(self, request, short_url):
        recipe = get_object_or_404(Recipe, short_url=short_url)
        serializer = RecipeSerializer(recipe, context={"request": request})
        return Response(serializer.data)
