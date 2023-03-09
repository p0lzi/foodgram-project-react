import re

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipe.models import Basket, Favorite, Ingredient, Recipe, Tag
from users.models import Subscribe, User
from .filters import RecipeFilter
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          SubscriptionsSerializer, TagSerializer)


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
    ordering = ('id',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    @staticmethod
    def obj_create(serializer, request, pk):
        serializer = serializer(data={'recipe_id': pk,
                                      'user_id': request.user.pk})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def send_file(ingredients):
        text = ('shopping cart is empty' if not ingredients else
                '\n'.join([
                    (f'{obj.get("recipe__ingredients__ingredient__name")}: '
                     f'{obj.get("recipe__ingredients__amount__sum")}')
                    for obj in ingredients]))
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename=foodgram_shopping_cart.txt')
        return response

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = request.user.baskets.prefetch_related(
            'recipe').values(
            'recipe__ingredients__ingredient__name').annotate(
            Sum('recipe__ingredients__amount')).order_by(
            'recipe__ingredients__ingredient__name')
        return self.send_file(ingredients)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        return self.obj_create(ShoppingCartSerializer, request, pk)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk):
        get_object_or_404(Basket, recipe_id=pk, user_id=request.user.pk
                          ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self.obj_create(FavoriteSerializer, request, pk)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk):
        get_object_or_404(Favorite, recipe_id=pk, user_id=request.user.pk
                          ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SubscriptionsSerializer
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        return User.objects.filter(followers__user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True, context={
                'user': request.user,
                'recipes_limit': (
                    lambda obj: int(obj)
                    if re.fullmatch(r"^\d+$", obj) else None)(
                    request.query_params.get('recipes_limit', ''))})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SubscribeView(APIView):

    @staticmethod
    def post(request, user_id):
        serializer = SubscribeSerializer(data={
            'author_id': user_id,
            'user_id': request.user.pk})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete(request, user_id):
        get_object_or_404(Subscribe, author_id=user_id, user_id=request.user.pk
                          ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
