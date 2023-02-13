from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator
from recipe.models import Recipe, Ingredient, Tag, IngredientInRecipe
from users.models import User, Follow
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    """ Сериализатор для работы с пользователями через права админа. """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if isinstance(user, AnonymousUser):
            return False
        return Follow.objects.filter(
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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientSerializerForRecipe(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientSerializerForRecipe(many=True)

    class Meta:
        model = Recipe
        fields = "__all__"

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')



