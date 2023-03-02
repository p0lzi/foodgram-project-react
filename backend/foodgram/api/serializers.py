import base64
from django.core import exceptions
from django.core.files.base import ContentFile
import django.contrib.auth.password_validation as validators
from rest_framework import serializers
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import authenticate

from recipe.models import (Recipe, Ingredient, Tag, IngredientInRecipe,
                           TagOfRecipes, Favorites, Basket)
from users.models import User, Subscribe


class UserSerializer(serializers.ModelSerializer):
    """ Сериализатор для работы с пользователями через права админа. """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = (self.context.get('request').user
                if self.context.get('request') else self.root.instance.author)
        if isinstance(user, AnonymousUser):
            return False
        return Subscribe.objects.filter(
            author__username=obj,
            user=user).exists()


class SelfUserSerializer(serializers.ModelSerializer):
    """ Сериализатор для работы с пользователем при запросе к /me/. """

    username = serializers.ReadOnlyField()
    role = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )


class UserRegisterSerializer(serializers.ModelSerializer):
    """ Сериализатор для проверки данных пользователей для регистрации."""

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {
            "password":
                {"write_only": True}
        }


class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        label="Email",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label="Token",
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=User.objects.get(email=email).username,
                password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = f'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    current_password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, data):
        new_password = data.get('new_password')
        current_password = data.get('current_password')
        user = self.context.get('request').user
        if not user.check_password(
                current_password):
            raise serializers.ValidationError(
                {"current_password": "Invalid password"})
        try:
            validators.validate_password(password=new_password,
                                         user=user)
        except exceptions.ValidationError as error:
            raise serializers.ValidationError(
                {"new_password": list(error.messages)})
        return data


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
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "name", "measurement_unit", "amount")

    @staticmethod
    def get_name(obj):
        return Ingredient.objects.get(pk=obj.ingredient_id).name

    @staticmethod
    def get_measurement_unit(obj):
        return Ingredient.objects.get(pk=obj.ingredient_id).measurement_unit


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient_id")

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "amount")

    def validate_id(self, value):
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError('Нет такого ингридиента')
        return value


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr),
                               name=f"image{self.root.instance.id}.{ext}")
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    # tags = TagSerializer(many=True)
    # author = UserSerializer()
    # ingredients = IngredientInRecipeSerializer(many=True)
    # is_favorited = serializers.SerializerMethodField()
    # is_in_shopping_cart = serializers.SerializerMethodField()
    # image = Base64ImageField()

    class Meta:
        model = Recipe
        # fields = (
        #     "id", "tags", "author", "ingredients", "is_favorited",
        #     "is_in_shopping_cart", "name", "image", "text", "cooking_time",)
        fields = ("name", "created")

    def get_is_favorited(self, obj):
        user = (self.context.get('request').user
                if self.context.get('request') else self.root.instance.author)
        if isinstance(user, AnonymousUser):
            return False
        return Favorites.objects.filter(
            recipe__name=obj,
            user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = (self.context.get('request').user
                if self.context.get('request') else self.root.instance.author)
        if isinstance(user, AnonymousUser):
            return False
        return Basket.objects.filter(
            recipe__name=obj,
            user=user).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "ingredients", "tags", "image", "name", "text", "cooking_time")

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance)
        return serializer.data

    def create(self, validated_data):
        ingredients_in_recipe = validated_data.pop('ingredients')
        tags_in_recipe = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_in_recipe in ingredients_in_recipe:
            IngredientInRecipe.objects.create(recipe=recipe,
                                              **ingredient_in_recipe)
        for tag_in_recipe in tags_in_recipe:
            TagOfRecipes.objects.create(recipe=recipe, tag=tag_in_recipe)

        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        if 'tags' in validated_data:
            instance.tags.set(validated_data.pop('tags'))
        if 'ingredients' in validated_data:
            instance.ingredients.set([
                IngredientInRecipe.objects.get_or_create(
                    recipe=instance, **ingredient)[0]
                for ingredient in validated_data.pop('ingredients')
            ])
        instance.save()
        return instance


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

    def get_recipes(self):
        return RecipeForUserSerializer(many=True, read_only=True)

    @staticmethod
    def get_recipes_count(user):
        return user.recipes.count()

    def get_is_subscribed(self, obj):
        user = (self.context.get('user') if self.context.get('user')
                else self.context.get('request').user)
        if isinstance(user, AnonymousUser):
            return False
        return Subscribe.objects.filter(
            author__username=obj,
            user=user).exists()


class SubscribeCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = ("user_id", "author_id")

    def validate_author_id(self, value):
        print(f"value= {value}")
        if not User.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Нет такого пользователя')
        return value

    def to_representation(self, instance):
        serializer = SubscriptionsSerializer(instance,
                                             context={"user": self.request.user})
        return serializer.data

    # def create(self, validated_data):
    #     ingredients_in_recipe = validated_data.pop('ingredients')
    #     tags_in_recipe = validated_data.pop('tags')
    #     recipe = Recipe.objects.create(**validated_data)
    #     for ingredient_in_recipe in ingredients_in_recipe:
    #         IngredientInRecipe.objects.create(recipe=recipe,
    #                                           **ingredient_in_recipe)
    #     for tag_in_recipe in tags_in_recipe:
    #         TagOfRecipes.objects.create(recipe=recipe, tag=tag_in_recipe)
    #
    #     return recipe