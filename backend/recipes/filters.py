from django_filters import rest_framework as filters

from .models import Recipe, Favourites, Ingredient, ShoppingList


class RecipeFilter(filters.FilterSet):
    author = filters.NumberFilter(
        field_name='author__id', lookup_expr='exact')
    tags = filters.CharFilter(field_name='tags__slug', lookup_expr='exact')
    is_favorited = filters.BooleanFilter(
        field_name='favourites', method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='shoppinglist', method='get_is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        recipes = []

        for item in Favourites.objects.filter(user=self.request.user):
            recipes.append(queryset.filter(id=item.recipe_id))
        
        if not recipes:
            favorite_recipe = Recipe.objects.none()
        elif len(recipes) == 1:
            favorite_recipe = recipes[0]
        else:
            favorite_recipe = recipes[0].union(*recipes[1:])

        if value:
            return favorite_recipe
        elif favorite_recipe:
            return Recipe.objects.all().difference(favorite_recipe)
        return Recipe.objects.all()
        
    
    def get_is_in_shopping_cart(self, queryset, name, value):
        recipes = []

        for item in ShoppingList.objects.filter(user=self.request.user):
            recipes.append(queryset.filter(shoppinglist=item.id))
        favorite_recipe = recipes[0].union(*recipes[1:])
        if value:
            return favorite_recipe
        return Recipe.objects.all().difference(favorite_recipe)

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']
    

