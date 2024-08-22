import base64
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
# from ingredients.models import Ingredient
# from ingredients.serializers import IngredientSerializer
from rest_framework import serializers
from users.serializers import UserSerializer

from .models import (Favourites, IngredientsRecipe, Recipe, ShoppingList, Tag,
                     TagsReciep, Ingredient)
from rest_framework.validators import UniqueTogetherValidator


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
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=ToDoItem.objects.all(),
        #         fields=['list', 'position']
        #     )
        # ]

        # fields = ('id', 'volume')


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
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')

    # read_only_fields = ('author',)

    def get_is_favorited(self, obj) -> bool:
        return Favourites.objects.filter(
            user=self.context.get('request').user.id,
            recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj) -> bool:
        return ShoppingList.objects.filter(
            user=self.context.get('request').user.id,
            recipe=obj).exists()

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user  # method get
        if ('tags' not in self.initial_data
                or 'ingredients' not in self.initial_data):
            raise serializers.ValidationError(
                'Поля tags и ingredients являются обязательными.')

        tags = self.initial_data.pop('tags')
        ingredients = self.initial_data.pop('ingredients')

        ingredient_ips = [item['id'] for item in ingredients]
        # if not tags:
        #     raise serializers.ValidationError(
        #         'Поле tags не должно быть пустым.')
        if not ingredients:
            raise serializers.ValidationError(
                'Поле ingredients не должно быть пустым.')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'В поле tags не должно быть повторяющихся тегов.')
        if len(ingredients) != len(set(ingredient_ips)):
            raise serializers.ValidationError(
                'В поле ingredients не должно быть повторяющихся ингредиентов.')

        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            if not Tag.objects.filter(id=tag).exists():
                raise serializers.ValidationError(
                    'Указанного тега не существует.')
            TagsReciep.objects.create(
                tag=get_object_or_404(Tag, id=tag), recipe=recipe)

        for ingredient in ingredients:
            getting_amount = ingredient.get('amount')
            if not getting_amount:
                raise serializers.ValidationError(
                    'Поле amount в поле ingredients является обязательным.')
            if not Ingredient.objects.filter(id=ingredient.get('id')).exists():
                raise serializers.ValidationError(
                    'Указанного ингредиента не существует.')
            IngredientsRecipe.objects.create(
                ingredient=get_object_or_404(Ingredient, id=ingredient.get('id')), amount=getting_amount, recipe=recipe)

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

        if 'tags' in self.initial_data:
            tags = self.initial_data.pop('tags')
            lst = []
            for tag in tags:
                current_tag = get_object_or_404(Tag, id=tag)
                lst.append(current_tag)
            instance.tags.set(lst)
        else:
            raise serializers.ValidationError(
                'Поле tags является обязательным.')

        if 'ingredients' in self.initial_data:
            ingredients = self.initial_data.pop('ingredients')
            ingredient_ids = []
            for ingredient in ingredients:
                ingredient_id = get_object_or_404(
                    Ingredient, id=ingredient.get('id')).id
                ingredient_instance, created = IngredientsRecipe.objects.update_or_create(
                    ingredient_id=ingredient_id,
                    recipe_id=self.instance.id,
                    defaults=dict(
                        amount=ingredient.get('amount'))
                )
                ingredient_ids.append(ingredient_instance.id)
        else:
            raise serializers.ValidationError(
                'Поле ingredients является обязательным.')
        instance.ingredients.set(ingredient_ids)

        instance.save()

        return instance
    
    def validate(self, data):#------------------------------------Валидацию!
        request = self.context
        tags = self.initial_data['tags']
        if not tags:
            raise serializers.ValidationError(
                'Поле tags не должно быть пустым.')
        return super().validate(data)


class FavoriteSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True)

    class Meta:
        model = Favourites
        fields = ('id', 'name', 'image', 'cooking_time')
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Favourites.objects.all(),
        #         fields=['user', 'recipe']
        #     )
        # ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user  # method get
        validated_data['recipe'] = Recipe.objects.get(
            id=self.context['id'])
        favorite = Favourites.objects.create(**validated_data)
        # favorite = Favourites.objects.create(user=self.context['request'].user)
        # favorite.recipe.add(Recipe.objects.get(
        #     id=self.initial_data.get('id')))

        return favorite

    def validate(self, data):
        request = self.context['request']
        # print(self.context['request'].id)
        recipe = get_object_or_404(Recipe, id=self.context['id'])
        if Favourites.objects.filter(user=request.user, recipe=recipe).exists():
            raise serializers.ValidationError(
                f'Данный рецепт уже добавлен в избранное!'
            )
        return data


class ShoppingListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True)

    class Meta:
        model = ShoppingList
        fields = ('id', 'name', 'image', 'cooking_time')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user  # method get
        validated_data['recipe'] = Recipe.objects.get(
            id=self.context['id'])
        cart = ShoppingList.objects.create(**validated_data)
        return cart

    def validate(self, data):
        request = self.context['request']
        recipe = get_object_or_404(Recipe, id=self.context['id'])
        if ShoppingList.objects.filter(user=request.user, recipe=recipe).exists():
            raise serializers.ValidationError(
                f'Данный рецепт уже добавлен в список покупок!'
            )
        return data
