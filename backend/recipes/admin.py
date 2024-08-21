from django.contrib import admin

from .models import Tag, Recipe, Favourites, ShoppingList, TagsReciep, IngredientsRecipe, Ingredient


class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ['short_url', 'count_favorite']
    list_display = ('name', 'author')
    list_filter = ('tags', )
    empty_value_display = 'Не заполнено'
    search_fields = ['name', 'author__username']

    @admin.display(description="У пользователей в избранном", )
    def count_favorite(self, obj):
        return Favourites.objects.filter(recipe_id=obj.id).count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ['name']


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favourites)
admin.site.register(ShoppingList)
admin.site.register(TagsReciep)
admin.site.register(IngredientsRecipe)
