import re
from io import StringIO

from django.http import HttpResponse
from djoser.views import UserViewSet
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.generics import DestroyAPIView, CreateAPIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter

from recipe.models import Recipe, Tag, Ingredient
from users.models import User, Subscribe
from .permissions import IsUserOrAdmin
from .serializers import (TagSerializer,
    # SelfUserSerializer,
    # UserRegisterSerializer,
                          UserSerializer,
                          CustomAuthTokenSerializer, RecipeSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          SubscriptionsSerializer,
                          RecipeForUserSerializer, SetPasswordSerializer,
                          SubscribeCreateSerializer)
from .filters import RecipeFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError


class CreateListRetrieveViewSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    """ Создаем базовый вью сет. """
    pass


class CreateDestroyViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    pass


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.filter()
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = RecipeFilter
    queryset = Recipe.objects.all()
    ordering = ('-created',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return RecipeCreateSerializer
        return RecipeSerializer


class DownloadShoppingCartView(APIView):
    def get(self, request):
        file = StringIO()
        shopping_cart = {}
        for recipe in request.user.basket.prefetch_related("recipe"):
            ingredients = recipe.ingredients.select_related("name", "amount")
        return HttpResponse(content='file', status=200)


class SubscriptionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SubscriptionsSerializer
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        print(self.request.user)
        return User.objects.filter(follower__user=self.request.user)

    def list(self, request, *args, **kwargs):
        serializer = SubscriptionsSerializer(
            self.get_queryset(), many=True, context={
                "user": request.user,
                'recipes_limit': (
                    lambda obj: int(obj)
                    if re.fullmatch(r"^\d+$", obj) else None)(
                    request.query_params.get("recipes_limit"))})
        return Response(serializer.data)


class ShoppingCartView(APIView):

    @staticmethod
    def post(request, recipe_id):
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
            request.user.basket.create(recipe=recipe)
        except IntegrityError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"errors": f"Рецепт с id {recipe_id} есть в корзине"})
        except ObjectDoesNotExist:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"errors": f"Рецепт с id {recipe_id} не существует"})
        except AttributeError:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = RecipeForUserSerializer(recipe)
        return Response(serializer.data)

    @staticmethod
    def delete(request, recipe_id):
        try:
            request.user.basket.get(recipe_id=recipe_id).delete()
        except ObjectDoesNotExist:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"errors": f"рецепта с id {recipe_id} нет в корзине"})
        except AttributeError:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteRecipeView(APIView):

    @staticmethod
    def post(request, recipe_id):
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
            request.user.favorites.create(recipe=recipe)
        except IntegrityError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"errors": f"Рецепт с id {recipe_id} есть в избранном"})
        except ObjectDoesNotExist:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"errors": f"Рецепт с id {recipe_id} не существует"})
        except AttributeError:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = RecipeForUserSerializer(recipe)
        return Response(serializer.data)

    @staticmethod
    def delete(request, recipe_id):
        try:
            request.user.favorites.get(recipe_id=recipe_id).delete()
        except ObjectDoesNotExist:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"errors": f"рецепта с id {recipe_id} нет в избранном"})
        except AttributeError:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeView(APIView):

    @staticmethod
    def post(request, user_id):
        try:
            author = User.objects.get(pk=user_id)
            request.user.following.create(author_id=user_id)
        except IntegrityError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"errors": f"Автор с id {user_id} есть в подписках"})
        except ObjectDoesNotExist:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"errors": f"Автор с id {user_id} не существует"})
        except AttributeError:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = SubscriptionsSerializer(author,
                                             context={"user": request.user})
        return Response(serializer.data)

    @staticmethod
    def delete(request, user_id):
        try:
            request.user.following.get(author_id=user_id).delete()
        except ObjectDoesNotExist:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"errors": f"Автор с id {user_id} нет в подписках"})
        except AttributeError:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return Response(status=status.HTTP_204_NO_CONTENT)


# class UserViewSet(CreateListRetrieveViewSet):
#     """ Вью сет для взаимодействия с пользователями с помощью админа. """
#     queryset = User.objects.all()
#
#     def get_permissions(self):
#         if self.action == 'retrieve':
#             return permissions.IsAuthenticated(),
#         return permissions.AllowAny(),
#
#     def get_serializer_class(self):
#         if self.action == 'create':
#             return UserRegisterSerializer
#         return UserSerializer
#
#     @action(detail=False, url_path='me', url_name='me',
#             methods=('GET',), permission_classes=[IsUserOrAdmin])
#     def get_me(self, request, *args, **kwargs):
#         """ Метод для обработки запросов к /me/"""
#         user = User.objects.get(username=request.user)
#         serializer = SelfUserSerializer(instance=user, data=request.data)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data = serializer.validated_data
#         password = data.pop('password')
#         user = User.objects.create(**data)
#         user.set_password(password)
#         user.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# class CustomObtainAuthToken(CreateAPIView):
#     """ Вью для получения JWT токена пользователем. """
#     serializer_class = CustomAuthTokenSerializer
#     permission_classes = (permissions.AllowAny,)
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.validated_data['user']
#             token = RefreshToken.for_user(user)
#             return Response({'auth_token': str(token.access_token)})
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomDestroyToken(DestroyAPIView):

    def delete(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            Response(status=status.HTTP_401_UNAUTHORIZED)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SetPassword(CreateAPIView):
    serializer_class = SetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
