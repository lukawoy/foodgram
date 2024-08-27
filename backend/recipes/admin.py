from django.contrib import admin

from .models import (
    Tag, Recipe, Favourites, ShoppingList,
    TagsReciep, IngredientsRecipe, Ingredient
)


class TagInline(admin.TabularInline):
    model = TagsReciep
    extra = 2


class IngredientInline(admin.TabularInline):
    model = IngredientsRecipe
    extra = 3


class RecipeAdmin(admin.ModelAdmin):
    inlines = (
        TagInline, IngredientInline
    )

    readonly_fields = ['short_url', 'count_favorite', 'pub_date']
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


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ['name', 'slug']


class FavouritesAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    search_fields = ['recipe__name', 'user__username']


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favourites, FavouritesAdmin)
admin.site.register(ShoppingList, FavouritesAdmin)
# admin.site.register(TagsReciep)
# admin.site.register(IngredientsRecipe)
