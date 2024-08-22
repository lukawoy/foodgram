from rest_framework import serializers, validators
from django.contrib.auth import get_user_model
from .models import Follow
import base64
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from rest_framework.relations import SlugRelatedField
from .validators import FollowSelfSubscriptionValidator
from recipes.models import Recipe

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta():
        model = User
        fields = ('avatar', )

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        # obj = User.objects.filter(username=self.context.get('user')).update(avatar=validated_data['avatar'])

        return instance


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta():
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )


    def get_is_subscribed(self, obj) -> bool:
        return Follow.objects.filter(
            user=obj.id,
            following=self.context.get('request').user.id).exists()

    # def validate(self, data):
    #     request = self.context['request']
    #     print(request)
    #     recipe = get_object_or_404(User, username=request.user.username)
        # if Favourites.objects.filter(user=request.user, recipe=recipe).exists():
        #     raise serializers.ValidationError(
        #         f'Данный рецепт уже добавлен в избранное!'
        #     )
        return data

        # return super().validate(attrs)


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {"password": {"write_only": True}}
    
    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(UserSerializer):
    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

    def get_recipes_count(self, obj) -> int:
        return Recipe.objects.filter(author=obj).count()
    

    # def create(self, validated_data):
    #     print(self.context)
    #     # following_id
    #     # user_id = self.context.

    #     following = Follow.objects.create(following_id=id, user_id=request.user.id)
    #     return following

    