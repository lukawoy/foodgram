import base64
import os

from dotenv import load_dotenv

from rest_framework import serializers

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

from users.serializers import UserSerializer
from .models import (
    Favourites, Ingredient, IngredientsRecipe, Recipe,
    ShoppingList, Tag, TagsReciep
)

load_dotenv(override=True)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredredientsRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = IngredientsRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ['amount',]


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(many=False, read_only=True)
    ingredients = IngredredientsRecipeSerializer(
        many=True, read_only=True, source='ingredientsrecipe_set')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj) -> bool:
        return Favourites.objects.filter(
            user=self.context.get('request').user.id,
            recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj) -> bool:
        return ShoppingList.objects.filter(
            user=self.context.get('request').user.id,
            recipe=obj).exists()

    def create(self, validated_data):
        validated_data['author'] = self.context.get('request').user

        tags = self.initial_data.pop('tags')
        ingredients = self.initial_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            TagsReciep.objects.create(
                tag=get_object_or_404(Tag, id=tag), recipe=recipe)

        for ingredient in ingredients:
            IngredientsRecipe.objects.create(
                ingredient=get_object_or_404(
                    Ingredient,
                    id=ingredient.get('id')),
                amount=ingredient.get('amount'),
                recipe=recipe
            )
        return recipe

    def update(self, instance, validated_data):
        if instance.author != self.context['request'].user:
            raise serializers.ValidationError(
                'Редактировать можно только свои рецепты.')

        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get(
            'text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)

        tags = self.initial_data.pop('tags')
        lst = []
        for tag in tags:
            current_tag = get_object_or_404(Tag, id=tag)
            lst.append(current_tag)
        instance.tags.set(lst)

        ingredients = self.initial_data.pop('ingredients')
        ingredient_ids = []
        for ingredient in ingredients:
            ingredient_instance = get_object_or_404(
                Ingredient, id=ingredient.get('id'))
            obj, created = IngredientsRecipe.objects.update_or_create(
                ingredient=ingredient_instance,
                recipe=self.instance,
                defaults={'amount': ingredient.get('amount')})
            ingredient_ids.append(ingredient_instance)
        instance.ingredients.set(ingredient_ids)
        instance.save()
        return instance

    def validate(self, data):
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                'Поле tags является обязательным и не должно быть пустым.')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'В поле tags не должно быть повторяющихся тегов.')
        for tag in tags:
            if not Tag.objects.filter(id=tag).exists():
                raise serializers.ValidationError(
                    'Указанного тега не существует.')

        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Поле ingredients является обязательным '
                'и не должно быть пустым.')
        ingredient_ips = [item['id'] for item in ingredients]
        if len(ingredients) != len(set(ingredient_ips)):
            raise serializers.ValidationError(
                'В поле ingredients не должно быть '
                'повторяющихся ингредиентов.')
        for ingredient in ingredients:
            if not ingredient.get('amount'):
                raise serializers.ValidationError(
                    'Поле amount в поле ingredients является обязательным.')
            if not Ingredient.objects.filter(id=ingredient.get('id')).exists():
                raise serializers.ValidationError(
                    'Указанного ингредиента не существует.')

        return super().validate(data)


class FavoriteSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True)

    class Meta:
        model = Favourites
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image_url(self, obj):
        if obj.recipe.image:
            return f'https://{os.getenv("DOMAIN")}{obj.recipe.image.url}'
        return None

    def validate(self, data):
        recipe = get_object_or_404(
            Recipe,
            id=self.context['view'].kwargs.get('recipe_id')
        )

        if Favourites.objects.filter(
                user=self.context.get('request').user,
                recipe=recipe).exists():
            raise serializers.ValidationError(
                'Данный рецепт уже добавлен в избранное!')
        return data


class ShoppingListSerializer(FavoriteSerializer):
    class Meta(FavoriteSerializer.Meta):
        model = ShoppingList

    def validate(self, data):
        recipe = get_object_or_404(
            Recipe,
            id=self.context['view'].kwargs.get('recipe_id')
        )

        if ShoppingList.objects.filter(
                user=self.context.get('request').user,
                recipe=recipe).exists():
            raise serializers.ValidationError(
                'Данный рецепт уже добавлен в список покупок!')
        return data
