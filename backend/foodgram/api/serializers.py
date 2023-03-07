from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipe.models import (Basket, Favorite, Ingredient, IngredientInRecipe,
                           Recipe, Tag, TagOfRecipes)
from users.models import Subscribe, User


class UserSerializer(serializers.ModelSerializer):
    """ Сериализатор для работы с пользователями через права админа. """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.followers.filter(user=obj).exists())


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient_id")
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient_id")
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "amount")

    @staticmethod
    def validate_id(value):
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError('Нет такого ингридиента')
        return value

    @staticmethod
    def validate_amount(value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество должно быть больше 0')
        return value


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientInRecipeSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id", "tags", "author", "ingredients", "is_favorited",
            "is_in_shopping_cart", "name", "image", "text", "cooking_time",)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.favorites.filter(
                    recipe__name=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.baskets.filter(
                    recipe__name=obj).exists())


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            "ingredients", "tags", "image", "name", "text", "cooking_time")

    def to_representation(self, instance):
        return RecipeSerializer(instance).data

    @staticmethod
    def validate_ingredients(value):
        errors = []
        if not value:
            errors.append("Рецепт не может быть без ингредиентов")
        if not (lambda elems: True if len(elems) == len(set(
                [elem.get('ingredient_id') for elem in elems])) else False)(
                    value):
            errors.append("Набор ингредиентов должен быть уникальным")
        if errors:
            raise serializers.ValidationError(errors)
        return value

    @staticmethod
    def validate_tags(value):
        errors = []
        if not value:
            errors.append("Необходимо выбрать тег")
        if not (lambda elems: True
                if len(elems) == len(set(elems)) else False)(value):
            errors.append("Набор тегов должен быть уникальным")
        if errors:
            raise serializers.ValidationError(errors)
        return value

    @staticmethod
    def validate_cooking_time(value):
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0')
        return value

    @staticmethod
    def set_ingredients(instance, ingredients):
        instance.ingredients.bulk_create([
            IngredientInRecipe(recipe=instance, **ingredient)
            for ingredient in ingredients])

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context.get("request").user)
        self.set_ingredients(recipe, ingredients)
        for tag in tags:
            TagOfRecipes.objects.create(recipe=recipe, tag=tag)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            instance.tags.set(validated_data.pop('tags'))
        if 'ingredients' in validated_data:
            instance.ingredients.all().delete()
            self.set_ingredients(instance, validated_data.pop('ingredients'))
        return super().update(instance, validated_data)


class RecipeForUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  "is_subscribed", 'recipes', 'recipes_count')
        model = User

    def get_recipes(self, obj):
        return RecipeForUserSerializer(
            obj.recipes.order_by("-created")[:self.context.get(
                'recipes_limit')],
            many=True, read_only=True).data

    @staticmethod
    def get_recipes_count(user):
        return user.recipes.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.followers.filter(user=obj).exists())


class ShoppingCartSerializer(serializers.ModelSerializer):
    recipe_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Basket
        fields = ("recipe_id", "user_id")

    def validate(self, attrs):
        if Basket.objects.filter(user_id=attrs["user_id"],
                                 recipe_id=attrs["recipe_id"]).exists():
            raise serializers.ValidationError(
                'Рецепт уже есть в корзине у данного пользователя')
        return attrs

    def to_representation(self, instance):
        return RecipeForUserSerializer(instance.recipe,
                                       context={
                                           "user": instance.user}).data


class FavoriteSerializer(serializers.ModelSerializer):
    recipe_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Favorite
        fields = ("recipe_id", "user_id")

    def validate(self, attrs):
        if Favorite.objects.filter(user_id=attrs["user_id"],
                                   recipe_id=attrs["recipe_id"]).exists():
            raise serializers.ValidationError(
                'Рецепт уже есть в избранном у данного пользователя')
        return attrs

    def to_representation(self, instance):
        return RecipeForUserSerializer(instance.recipe,
                                       context={
                                           "user": instance.user}).data


class SubscribeSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Subscribe
        fields = ("author_id", "user_id")

    @staticmethod
    def validate_author_id(value):
        if not User.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Нет такого пользователя')
        return value

    def validate(self, attrs):
        if Subscribe.objects.filter(user_id=attrs["user_id"],
                                    author_id=attrs["author_id"]).exists():
            raise serializers.ValidationError(
                'Подписка уже есть у данного пользователя')
        return attrs

    def to_representation(self, instance):
        return SubscriptionsSerializer(instance.author,
                                       context={
                                           "user": instance.user}).data
