# Generated by Django 3.2.3 on 2024-09-02 20:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("recipes", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="shoppinglist",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="shoppinglist_user",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Пользователь",
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recipes_author",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Автор",
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="ingredients",
            field=models.ManyToManyField(
                through="recipes.IngredientsRecipe",
                to="recipes.Ingredient",
                verbose_name="Ингредиенты",
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="tags",
            field=models.ManyToManyField(
                through="recipes.TagsReciep", to="recipes.Tag", verbose_name="Теги"
            ),
        ),
        migrations.AddField(
            model_name="ingredientsrecipe",
            name="ingredient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="amount_ingredient",
                to="recipes.ingredient",
                verbose_name="Ингредиент",
            ),
        ),
        migrations.AddField(
            model_name="ingredientsrecipe",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ingredients_recipe",
                to="recipes.recipe",
                verbose_name="Рецепт",
            ),
        ),
        migrations.AddField(
            model_name="favourites",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favorites_recipe",
                to="recipes.recipe",
                verbose_name="Рецепт",
            ),
        ),
        migrations.AddField(
            model_name="favourites",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favorites",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Пользователь",
            ),
        ),
        migrations.AddConstraint(
            model_name="ingredientsrecipe",
            constraint=models.UniqueConstraint(
                fields=("ingredient", "recipe"), name="Unique pair ingredient-recipe"
            ),
        ),
    ]
