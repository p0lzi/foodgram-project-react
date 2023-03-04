import re
from io import StringIO

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipe.models import Ingredient, Recipe, Tag
from rest_framework import mixins, status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User

from .filters import RecipeFilter
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeForUserSerializer, RecipeSerializer,
                          SubscriptionsSerializer, TagSerializer)


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
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    filter_backends = [SearchFilter]
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    search_fields = ('^name', '$name')


class RecipeViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = RecipeFilter
    permission_classes = (AllowAny,)
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
        shopping_cart = {}
        ingredients = request.user.basket.prefetch_related(
            "recipe"
        ).values_list(
            'recipe__ingredients__ingredient__name',
            'recipe__ingredients__amount')
        if ingredients:
            for ingredient, amount in ingredients:
                if ingredient in shopping_cart:
                    shopping_cart[ingredient] += amount
                else:
                    shopping_cart[ingredient] = amount
            result = [f"{k}: {v}\n" for k, v in shopping_cart.items()]
        else:
            result = ["shopping cart is empty"]
        buffer = StringIO()
        buffer.writelines(result)
        buffer.seek(0)
        return FileResponse(buffer.read(),
                            content_type='text/plain',
                            as_attachment=True,
                            filename='shopping_cart.txt',
                            status=status.HTTP_200_OK)


class SubscriptionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SubscriptionsSerializer
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        return User.objects.filter(follower__user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True, context={
                "user": request.user,
                'recipes_limit': (
                    lambda obj: int(obj)
                    if re.fullmatch(r"^\d+$", obj) else None)(
                    request.query_params.get("recipes_limit", ""))})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
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
