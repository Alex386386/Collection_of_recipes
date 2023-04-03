import base64

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.relations import StringRelatedField

from recipes.models import (Tag, Ingredient, Recipe, ShoppingCart, Favorite,
                            RecipeIngredient, RecipeTag)
from users.models import User, Subscription
from .utils import get_ingredients_dict


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.subscribed.filter(subscriber_id=user.id).exists()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed',
                  )


class CreateUserSerializer(UserCreateSerializer):
    """Класс сериализатор для создания юзера."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password',
                  )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Класс сериализатор тэгов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Класс сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели связи ингредиента и рецепта."""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeSerializerGet(serializers.ModelSerializer):
    """Класс сериализатор рецепта для запросов GET."""
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        ingredient_recipe = RecipeIngredient.objects.filter(recipe=obj.pk)
        result = IngredientRecipeSerializer(ingredient_recipe, many=True).data
        return result

    def get_is_favorited(self, obj):
        user_id = self.context.get('request').user.id
        return Favorite.objects.filter(
            user=user_id, recipe=obj.pk
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user_id = self.context.get('request').user.id
        return ShoppingCart.objects.filter(
            user=user_id, recipe=obj.pk
        ).exists()

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time',)
        model = Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Класс сериализатор для создания и удаления рецептов."""
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = IngredientRecipeSerializer(
        many=True
    )
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'author',
                  'tags', 'ingredients',
                  'image', 'text', 'cooking_time',
                  )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        if not ingredients:
            raise serializers.ValidationError(
                "Вы должны добавить хотя бы один ингредиент!")
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)

        ingredients_dict = get_ingredients_dict(ingredients)

        recipe_ingredients = []
        for ingredient_id, amount in ingredients_dict.items():
            current_ingredient, status = Ingredient.objects.get_or_create(
                pk=ingredient_id)
            recipe_ingredients.append(RecipeIngredient(
                ingredient=current_ingredient,
                recipe=recipe,
                amount=amount))
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

        recipe_tags = []
        for tag in tags:
            recipe_tags.append(RecipeTag(tag=tag, recipe=recipe))
        RecipeTag.objects.bulk_create(recipe_tags)

        return recipe

    def validate(self, data):
        ingredients = data.get('ingredients')
        author = self.context['request'].user
        text = data.get('text')
        name = data.get('name')

        ingredients_ids = [ingredient['ingredient']['id'] for ingredient in
                           ingredients]
        recipes = Recipe.objects.filter(author=author,
                                        text=text,
                                        name=name,
                                        ingredients__id__in=ingredients_ids)
        if recipes.exists():
            raise ValidationError('Рецепт уже существует в базе данных')
        return data

    def to_representation(self, instance):
        self.fields.pop('ingredients')
        self.fields.pop('tags')
        representation = super().to_representation(instance)
        representation['ingredients'] = IngredientRecipeSerializer(
            RecipeIngredient.objects.filter(recipe=instance), many=True).data
        representation['tags'] = TagSerializer(instance.tags, many=True).data
        return representation

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        if tags_data:
            instance.tags.clear()
            for tag in tags_data:
                instance.tags.add(tag)
        if ingredients_data:
            ingredients_dict = get_ingredients_dict(ingredients_data)
            RecipeIngredient.objects.filter(recipe=instance).delete()

            recipe_ingredients = []
            for ingredient_id, amount in ingredients_dict.items():
                current_ingredient, status = Ingredient.objects.get_or_create(
                    pk=ingredient_id)
                recipe_ingredients.append(RecipeIngredient(
                    ingredient=current_ingredient,
                    recipe=instance,
                    amount=amount))
            RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return instance


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Класс сериализатор для показания рецептов при выводе юзеров."""
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscriptionSerializer(serializers.ModelSerializer):
    """Класс сериализатор для подписок."""
    email = StringRelatedField(source='subscribed.email')
    id = serializers.IntegerField(source='subscribed.id', read_only=True)
    username = StringRelatedField(source='subscribed.username')
    first_name = StringRelatedField(source='subscribed.first_name')
    last_name = StringRelatedField(source='subscribed.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'is_subscribed', 'first_name',
                  'last_name', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(
            subscriber_id=obj.subscriber.id, subscribed_id=obj.subscribed.id
        ).exists()

    def get_recipes(self, obj):
        limit = self.context.get('request').query_params.get('recipes_limit')
        if limit is not None:
            recipes_limit = int(
                self.context.get('request').query_params.get('recipes_limit'))
            queryset = Recipe.objects.filter(
                author=obj.subscribed)[:recipes_limit]
            return ShortRecipeSerializer(queryset, many=True).data
        queryset = Recipe.objects.filter(author=obj.subscribed)
        return ShortRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        count = Recipe.objects.filter(author=obj.subscribed).count()
        return count

    def validate(self, data):
        """Проверка на повтор."""
        subscribed_id = self.context.get('subscribed_id')
        subscriber_id = self.context.get('request').user.id
        if subscriber_id == subscribed_id:
            raise serializers.ValidationError(
                'Невозможно подписаться на самого себя')
        if Subscription.objects.filter(
                subscriber_id=subscriber_id,
                subscribed_id=subscribed_id
        ).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя!')
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    """Класс сериализатор для добавления рецепта в список избранного."""
    id = serializers.IntegerField(source='recipe.id', read_only=True)
    name = StringRelatedField(source='recipe.name')
    image = StringRelatedField(source='recipe.image')
    cooking_time = StringRelatedField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        """Проверка на повтор."""
        recipe_id = self.context.get('recipe_id')
        user_id = self.context.get('request').user.id
        if Favorite.objects.filter(
                user_id=user_id, recipe_id=recipe_id).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранные!')
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Класс сериализатор для добавления рецепта в список покупок."""
    id = serializers.IntegerField(source='recipe.id', read_only=True)
    name = StringRelatedField(source='recipe.name')
    image = StringRelatedField(source='recipe.image')
    cooking_time = StringRelatedField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        """Проверка на повтор."""
        recipe_id = self.context.get('recipe_id')
        user_id = self.context.get('request').user.id
        if ShoppingCart.objects.filter(
                user_id=user_id, recipe_id=recipe_id).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок!')
        return data


class DownloadShoppingCartSerializer(serializers.ModelSerializer):
    """Класс сериализатор для скачивания списка покупок."""
    ingredients = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        ingredient_recipe = RecipeIngredient.objects.filter(
            recipe=obj.recipe.id)
        result = IngredientRecipeSerializer(ingredient_recipe, many=True).data
        return result

    class Meta:
        fields = ('ingredients',)
        model = ShoppingCart
