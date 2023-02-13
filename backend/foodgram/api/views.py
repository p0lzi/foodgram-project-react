from rest_framework import mixins, permissions, status, viewsets
from rest_framework.generics import CreateAPIView, DestroyAPIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from recipe.models import Recipe, Tag, Ingredient
from users.models import User
from .permissions import IsAdminOrReadOnly, IsCustomAdminUser, IsUserOrAdmin
from .serializers import (TagSerializer, SelfUserSerializer,
                          UserRegisterSerializer, UserSerializer,
                          CustomAuthTokenSerializer, RecipeSerializer,
                          IngredientSerializer)
from .filters import RecipeFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.schemas import ManualSchema
from rest_framework.authtoken.models import Token
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist

class CreateListRetrieveViewSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    """ Создаем базовый вью сет. """
    pass


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.filter()
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    # В postgresql
    # queryset = Ingredient.objects.distinct("name", "measurement_unit").all()
    # В sqlite
    distinct_name = Ingredient.objects.values(
        'name').annotate(name_count=Count('name'))
    distinct_measurement_unit = Ingredient.objects.values(
        'measurement_unit').annotate(
        measurement_unit_count=Count('measurement_unit'))
    queryset = Ingredient.objects.filter(
        name__in=[item['name'] for item in distinct_name],
        measurement_unit__in=[item['measurement_unit'] for item in
                              distinct_measurement_unit])
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class DownloadShoppingCartViewSet(viewsets.ModelViewSet):
    pass


class FavoriteRecipeViewSet(viewsets.ModelViewSet):
    pass


class SubscriptionsViewSet(viewsets.ModelViewSet):
    pass


class UserViewSet(CreateListRetrieveViewSet):
    """ Вью сет для взаимодействия с пользователями с помощью админа. """
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action == 'retrieve':
            return permissions.IsAuthenticated(),
        return permissions.AllowAny(),

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegisterSerializer
        return UserSerializer

    @action(detail=False, url_path='me', url_name='me',
            methods=('GET',), permission_classes=[IsUserOrAdmin])
    def get_me(self, request, *args, **kwargs):
        """ Метод для обработки запросов к /me/"""
        user = User.objects.get(username=request.user)
        serializer = SelfUserSerializer(instance=user, data=request.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomObtainAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


class CustomDestroyToken(DestroyAPIView):

    def delete(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            Response(status=status.HTTP_401_UNAUTHORIZED)
        return Response(status=status.HTTP_204_NO_CONTENT)
