from django_filters import rest_framework as filters

from .models import Recipe, Favourites


class RecipeFilter(filters.FilterSet):
    author = filters.CharFilter(
        field_name='author__username', lookup_expr='exact')
    tags = filters.CharFilter(field_name='tags__name', lookup_expr='exact')
    is_favorited = filters.BooleanFilter(
        field_name='favourites', method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='shoppinglist', method='get_is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        recipes = []

        for item in Favourites.objects.filter(user=self.request.user):
            recipes.append(queryset.filter(favourites=item.id))
        favorite_recipe = recipes[0].union(*recipes[1:])
        if value:
            return favorite_recipe
        return Recipe.objects.all().difference(favorite_recipe)
    
    def get_is_in_shopping_cart(self, queryset, name, value):
        return queryset

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']
