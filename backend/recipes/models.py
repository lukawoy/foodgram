import random

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from foodgram_backend.settings import (CHARACTERS, MINIMUM_COOKING_TIME_IN_MIN,
                                       TOKEN_LENGTH)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField('Тег', max_length=150, unique=True)
    slug = models.SlugField('Идентификатор', max_length=150, unique=True)

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=150, db_index=True)
    measurement_unit = models.CharField('Единица измерения', max_length=20)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField('Название', max_length=256)
    text = models.TextField('Описание')
    cooking_time = models.IntegerField(
        'Время приготовления (в минутах)', validators=[
            MinValueValidator(MINIMUM_COOKING_TIME_IN_MIN)])
    tags = models.ManyToManyField(
        Tag, verbose_name='Теги', through='TagsReciep')
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='Ингредиенты', through='IngredientsRecipe')
    image = models.ImageField(
        'Вид блюда',
        upload_to='recipes/images/',
        default=None
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Автор')
    short_url = models.CharField(
        'Короткая ссылка', max_length=3, unique=True, db_index=True)
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.short_url:
            while True:
                self.short_url = ''.join(
                    random.choices(
                        CHARACTERS,
                        k=TOKEN_LENGTH
                    )
                )
                if not Recipe.objects.filter(
                    short_url=self.short_url
                ).exists():
                    break
        super().save(*args, **kwargs)


class TagsReciep(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name='Тег')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')

    class Meta:
        verbose_name = 'связь тег-рецепт'
        verbose_name_plural = 'Связь тег-рецепт'

    def __str__(self):
        return f'Тег "{self.tag}" - рецепт "{self.recipe}"'


class IngredientsRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='amount_ingredient',
        verbose_name='Ингредиент')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')
    amount = models.IntegerField('Количество ингредиента')

    class Meta:
        verbose_name = 'связь ингредиент-рецепт'
        verbose_name_plural = 'Связь ингредиент-рецепт'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique pair ingredient-recipe')
        ]

    def __str__(self):
        return f'Ингредиент "{self.ingredient}" - рецепт "{self.recipe}"'


class Favourites(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.recipe.name} - {self.user.username}'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.recipe.name} - {self.user.username}'
