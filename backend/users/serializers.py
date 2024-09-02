import base64

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

from recipes.models import Recipe
from .models import Follow

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ("avatar",)

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "avatar",
        )

    def get_is_subscribed(self, obj) -> bool:

        return obj.followings_user.filter(
            following_id=self.context["request"].user.id
        ).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class FollowSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = Base64ImageField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
            "avatar",
        )
        read_only_fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes_count(self, obj) -> int:
        return obj.recipes_author.all().count()

    def get_recipes(self, obj):
        recipes = obj.recipes_author.all()
        serialize_recipes = []
        for recipe in recipes:
            serializer = ShortRecipeSerializer(recipe)
            serialize_recipes.append(serializer.data)

        recipes_limit = self.context["request"].GET.get("recipes_limit")
        if recipes_limit:
            if not recipes_limit.isdigit():
                raise serializers.ValidationError(
                    "Параметр recipes_limit должен быть "
                    "целым положительным числом."
                )
            return serialize_recipes[:int(recipes_limit)]

        return serialize_recipes

    def create(self, validated_data):
        following_id = validated_data.get("following_id")
        Follow.objects.create(
            following_id=following_id, user_id=validated_data.get("user_id")
        )
        return User.objects.get(id=following_id)

    def validate(self, data):
        user_id = self.context.get("request").user.id
        following_id = int(self.context["view"].kwargs.get("user_id"))
        following_user = get_object_or_404(User, id=following_id)

        if following_user.followings.filter(user_id=user_id).exists() or (
            user_id == following_id
        ):
            raise serializers.ValidationError(
                "Подписка уже существует или невозможна."
            )
        return {"following_id": following_id, "user_id": user_id}
