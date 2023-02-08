from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator
from recipe.models import Recipe, Ingredient, Tag
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """ Сериализатор для работы с пользователями через права админа. """

    # Переопределяем почту, чтобы проверять уникальность значений.
    email = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Пользователь с такой почтой уже существует.')]
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )


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
    """ Сериализатор для проверки данных пользователей при самостоятельной
    регистрации через токен. """

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, data):
        # Проверяем, что username не является me
        if data['username'] == 'me':
            raise serializers.ValidationError("Me is invalid username")
        return data


class ObtainUserTokenSerializer(serializers.ModelSerializer):
    """ Сериализатор для получения токена, когда пользователь уже
    зарегистрирован. """

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"

# class CategorySerializer(serializers.ModelSerializer):
#     """ Сериализатор для работы с категориями произведений. """
#
#     class Meta:
#         model = Category
#         fields = ('name', 'slug')
#         lookup_field = 'slug'
#         extra_kwargs = {
#             'url': {'lookup_field': 'slug'}
#         }
#
#
# class GenreSerializer(serializers.ModelSerializer):
#     """ Сериализатор для работы с жанрами произведений. """
#
#     class Meta:
#         model = Genre
#         fields = ('name', 'slug')
#         lookup_field = 'slug'
#         extra_kwargs = {
#             'url': {'lookup_field': 'slug'}
#         }
#
#
# class CreateTitleSerializer(serializers.ModelSerializer):
#     """ Сериализатор для создания произведений. """
#
#     category = SlugRelatedField(
#         slug_field='slug',
#         queryset=Category.objects.all(),
#     )
#     genre = SlugRelatedField(
#         many=True,
#         queryset=Genre.objects.all(),
#         slug_field='slug'
#     )
#
#     class Meta:
#         model = Title
#         fields = ('id', 'name', 'year', 'description', 'genre', 'category')
#
#
# class ReadTitleSerializer(serializers.ModelSerializer):
#     """ Сериализатор для чтения произведений. """
#
#     category = CategorySerializer()
#     genre = GenreSerializer(many=True)
#     rating = serializers.SerializerMethodField(method_name='get_rating')
#
#     class Meta:
#         model = Title
#         fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
#                   'category')
#
#     @staticmethod
#     def get_rating(obj):
#         """ Метод для просчитывания рейтинга произведений. """
#
#         reviews = Review.objects.filter(title_id=obj.id)
#         scores_for_title = (
#             title.score for title
#             in reviews
#         )
#         if reviews:
#             return sum(scores_for_title) / reviews.count()
#         return None
#
#
# class ReviewSerializer(serializers.ModelSerializer):
#     """ Сериализатор для работы с отзывами пользователей по произведениям. """
#
#     author = serializers.SlugRelatedField(
#         read_only=True,
#         slug_field='username',
#         default=serializers.CurrentUserDefault()
#     )
#
#     def validate(self, data):
#         request = self.context.get('request')
#         if request.method != 'POST':
#             return data
#
#         reviewer = request.user
#         title_id = self.context.get('view').kwargs.get('title_id')
#         title = get_object_or_404(Title, pk=title_id)
#
#         # Проверяем существует ли уже такой отзыв
#         if Review.objects.filter(author=reviewer, title=title).exists():
#             raise serializers.ValidationError(
#                 'Нельзя добавить второй отзыв на то же самое произведение.'
#             )
#         return data
#
#     class Meta:
#         model = Review
#         fields = ('id', 'text', 'author', 'score', 'pub_date',)
#
#
# class CommentSerializer(serializers.ModelSerializer):
#     """ Сериализатор для работы с комментариями пользователей к отзывам. """
#
#     author = serializers.SlugRelatedField(
#         read_only=True,
#         slug_field='username',
#         default=serializers.CurrentUserDefault()
#     )
#
#     class Meta:
#         model = Comment
#         fields = ('id', 'text', 'author', 'pub_date')
