from django_filters import rest_framework as filters

from .models import (
    Favourites, Ingredient, Recipe, ShoppingList, Tag
)


class RecipeFilter(filters.FilterSet):
    author = filters.NumberFilter(
        field_name='author__id', lookup_expr='exact')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        lookup_expr='exact',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        field_name='favourites', method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='shoppinglist', method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def _get_resipes(self, model, queryset, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()

        recipes = []
        for item in model.objects.filter(user=self.request.user):
            recipes.append(queryset.filter(id=item.recipe_id))

        if not recipes:
            qs_recipes = Recipe.objects.none()
        elif len(recipes) == 1:
            qs_recipes = recipes[0]
        else:
            qs_recipes = recipes[0].union(*recipes[1:])

        if value:
            return qs_recipes
        return Recipe.objects.all().difference(qs_recipes)

    def get_is_favorited(self, queryset, name, value):
        return self._get_resipes(Favourites, queryset, value)

    def get_is_in_shopping_cart(self, queryset, name, value):
        return self._get_resipes(ShoppingList, queryset, value)


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']
