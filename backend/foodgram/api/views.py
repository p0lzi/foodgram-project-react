import random

from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from recipe.models import Recipe, Tag, Ingredient
from users.models import User

# from .filters import TitleFilter
from .permissions import IsAdminOrReadOnly, IsCustomAdminUser, IsUserOrAdmin
from .serializers import (TagSerializer, ObtainUserTokenSerializer, SelfUserSerializer,
                          UserRegisterSerializer, UserSerializer)
# from .serializers import (CategorySerializer, CommentSerializer,
#                           CreateTitleSerializer, GenreSerializer,
#                           ReviewSerializer, ReadTitleSerializer)


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    """ Создаем базовый вью сет. """
    pass


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    pass


class DownloadShoppingCartViewSet(viewsets.ModelViewSet):
    pass


class FavoriteRecipeViewSet(viewsets.ModelViewSet):
    pass


class SubscriptionsViewSet(viewsets.ModelViewSet):
    pass


class IngredientsViewSet(viewsets.ModelViewSet):
    pass


class UserViewSet(viewsets.ModelViewSet):
    """ Вью сет для взаимодействия с пользователями с помощью админа. """

    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    permission_classes = (permissions.IsAuthenticated, IsCustomAdminUser,)
    lookup_field = 'username'
    lookup_value_regex = '[\\w.@+-]{1,150}'
    search_fields = ('username',)
    queryset = User.objects.all()

    @action(detail=False, url_path='me', url_name='me',
            methods=('GET', 'PATCH'), permission_classes=[IsUserOrAdmin])
    def get_me(self, request, *args, **kwargs):
        """ Метод для обработки запросов к /me/"""

        queryset = User.objects.get(username=request.user)
        serializer = SelfUserSerializer(instance=queryset, data=request.data)
        if serializer.is_valid():
            # Если patch, то сохраняем данные пользователя
            if request.method == 'PATCH':
                serializer.save(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterUser(CreateAPIView):
    """ Вью для самостоятельной регистрации пользователей. """

    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # Генерируем пятизначный код
            confirmation_code = random.randint(10000, 99999)
            User.objects.get_or_create(**serializer.validated_data,
                                       confirmation_code=confirmation_code)
            # Отправляем код на почту пользователя
            send_mail(
                'Confirmation code',
                f'Your confirmation code is {confirmation_code}',
                None,
                [serializer.validated_data.get('email')],
                fail_silently=False,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObtainUserToken(CreateAPIView):
    """ Вью для получения JWT токена пользователем. """

    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = ObtainUserTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(
                User, username=serializer.data.get('username'))
            code = serializer.data.get('confirmation_code')
            # Проверяем, что код совпадает отправленный пользователем
            # и сгенерированный автоматически совпадает
            if user.confirmation_code == code:
                token = RefreshToken.for_user(user)
                return Response({'access': str(token.access_token)})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class CategoryViewSet(CreateListDestroyViewSet):
#     """ Вью сет для взаимодействия с категориями. """
#
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     permission_classes = (IsAdminOrReadOnly,)
#     filter_backends = (filters.SearchFilter,)
#     search_fields = ('name',)
#     lookup_field = 'slug'
#
#
# class GenreViewSet(CreateListDestroyViewSet):
#     """ Вью сет для взаимодействия с жанрами. """
#
#     queryset = Genre.objects.all()
#     serializer_class = GenreSerializer
#     permission_classes = (IsAdminOrReadOnly,)
#     filter_backends = (filters.SearchFilter,)
#     search_fields = ('name',)
#     lookup_field = 'slug'
#
#
# class TitleViewSet(viewsets.ModelViewSet):
#     """ Вью сет для взаимодействия с произведениями. """
#
#     queryset = Title.objects.all()
#     permission_classes = (IsAdminOrReadOnly,)
#     filter_backends = (DjangoFilterBackend,)
#     # filterset_class = TitleFilter
#
#     def get_serializer_class(self):
#         if self.request.method == 'GET':
#             return ReadTitleSerializer
#         return CreateTitleSerializer
#
#

#
#
# class ReviewViewSet(viewsets.ModelViewSet):
#     """ Вью сет для взаимодействия с отзывами пользователей. """
#
#     permission_classes = (IsAuthenticatedOrReadOnly,)
#     serializer_class = ReviewSerializer
#
#     def get_title(self):
#         return get_object_or_404(Title, pk=self.kwargs.get('title_id'))
#
#     def get_queryset(self):
#         return self.get_title().reviews.all()
#
#     def perform_create(self, serializer):
#         serializer.save(author=self.request.user, title=self.get_title())
#
#     def perform_update(self, serializer):
#         if serializer.instance.author != self.request.user:
#             raise PermissionDenied('Изменить не свой отзыв нельзя')
#         super(ReviewViewSet, self).perform_update(serializer)
#
#     def perform_destroy(self, instance):
#         if not (instance.author == self.request.user
#                 or self.request.user.role == 'moderator'):
#             raise PermissionDenied('Удалить чужой отзыв нельзя')
#         super(ReviewViewSet, self).perform_destroy(instance)
#
#
# class CommentViewSet(ReviewViewSet):
#     """ Вью сет для взаимодействия с комментариями пользователей. """
#
#     serializer_class = CommentSerializer
#
#     def get_review(self):
#         return get_object_or_404(
#             Review,
#             pk=self.kwargs.get('review_id'),
#             title__pk=self.kwargs.get('title_id')
#         )
#
#     def get_queryset(self):
#         return self.get_review().comments.all()
#
#     def perform_create(self, serializer):
#         serializer.save(author=self.request.user, review=self.get_review())
