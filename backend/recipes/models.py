import random

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from foodgram_backend.settings import (
    CHARACTERS_FOR_SHORT_URL,
    MINIMUM_COOKING_TIME_IN_MIN,
    MAXIMUM_COOKING_TIME_IN_MIN,
    MINIMUM_AMOUNT,
    MAXIMUM_AMOUNT,
    SHORT_URL_LENGTH,
)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField("Тег", max_length=150, unique=True)
    slug = models.SlugField("Идентификатор", max_length=150, unique=True)

    class Meta:
        verbose_name = "тег"
        verbose_name_plural = "Теги"
        ordering = ["-name"]

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField("Название", max_length=150, db_index=True)
    measurement_unit = models.CharField("Единица измерения", max_length=20)

    class Meta:
        verbose_name = "ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ["-name"]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField("Название", max_length=256)
    text = models.TextField("Описание")
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления (в минутах)",
        validators=[
            MinValueValidator(MINIMUM_COOKING_TIME_IN_MIN),
            MaxValueValidator(MAXIMUM_COOKING_TIME_IN_MIN),
        ],
    )
    tags = models.ManyToManyField(
        Tag, verbose_name="Теги", through="TagsReciep"
    )
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name="Ингредиенты", through="IngredientsRecipe"
    )
    image = models.ImageField(
        "Вид блюда", upload_to="recipes/images/", default=None)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes_author",
        verbose_name="Автор",
    )
    short_url = models.CharField(
        "Короткая ссылка", max_length=3, unique=True, db_index=True
    )
    pub_date = models.DateTimeField(
        "Дата добавления", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.short_url:
            while True:
                self.short_url = "".join(
                    random.choices(CHARACTERS_FOR_SHORT_URL,
                                   k=SHORT_URL_LENGTH)
                )
                if not Recipe.objects.filter(
                        short_url=self.short_url).exists():
                    break
        super().save(*args, **kwargs)


class TagsReciep(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name="Тег")
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name="Рецепт")

    class Meta:
        verbose_name = "связь тег-рецепт"
        verbose_name_plural = "Связь тег-рецепт"
        ordering = ["-recipe"]

    def __str__(self):
        return f'Тег "{self.tag}" - рецепт "{self.recipe}"'


class IngredientsRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="amount_ingredient",
        verbose_name="Ингредиент",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="ingredients_recipe",
    )
    amount = models.PositiveSmallIntegerField(
        "Количество ингредиента",
        validators=[
            MinValueValidator(MINIMUM_AMOUNT),
            MaxValueValidator(MAXIMUM_AMOUNT),
        ],
    )

    class Meta:
        verbose_name = "связь ингредиент-рецепт"
        verbose_name_plural = "Связь ингредиент-рецепт"
        ordering = ["-recipe"]
        constraints = [
            models.UniqueConstraint(
                fields=["ingredient", "recipe"],
                name="Unique pair ingredient-recipe"
            )
        ]

    def __str__(self):
        return f"{self.ingredient} - {self.recipe}"


class Favourites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="favorites",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="favorites_recipe",
    )

    class Meta:
        verbose_name = "избранное"
        verbose_name_plural = "Избранное"
        ordering = ["-user"]

    def __str__(self):
        return f"{self.recipe.name} - {self.user.username}"


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="shoppinglist_user",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="shoppinglist_recipe",
    )

    class Meta:
        verbose_name = "список покупок"
        verbose_name_plural = "Списки покупок"
        ordering = ["-user"]

    def __str__(self):
        return f"{self.recipe.name} - {self.user.username}"
