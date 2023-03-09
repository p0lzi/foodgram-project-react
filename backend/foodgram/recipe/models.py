from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from users.models import User


class BaseModel(models.Model):
    """ Общая модель для классов рецепта, тегов и ингридиентов."""
    name = models.CharField(
        'Название', unique=True,
        max_length=settings.MAX_LENGTH_FOR_FIELDS_OF_MODELS)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название', max_length=settings.MAX_LENGTH_FOR_FIELDS_OF_MODELS)
    measurement_unit = models.CharField(
        'Мера измерения', max_length=settings.MAX_LENGTH_FOR_FIELDS_OF_MODELS)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиент'

    constraints = [
        models.UniqueConstraint(
            fields=('name', 'measurement_unit'),
            name='unique_name_measurement_unit'
        )
    ]

    def __str__(self):
        return self.name


class Tag(BaseModel):
    color = models.CharField(max_length=7,
                             validators=[
                                 RegexValidator(regex='^#[0-9A-F]{6,6}$')])
    slug = models.SlugField(
        'URL', unique=True,
        max_length=settings.MAX_LENGTH_FOR_FIELDS_OF_MODELS,
        validators=[
            RegexValidator(regex='[-a-zA-Z0-9_]+')])

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Recipe(BaseModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    text = models.TextField()
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images/',
        blank=True,
        null=True,
        default=None,
        help_text='Загрузите картинку')
    tags = models.ManyToManyField(
        Tag,
        through='TagOfRecipes',
        verbose_name='Ингридиенты'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(1, 'Число дожно быть больше 1')])

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)


class IngredientInRecipe(models.Model):
    """ Связующая модель для рецептов и ингредиентов."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='ingredients',
                               verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(1, 'Число дожно быть больше 1')])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            )
        ]


class TagOfRecipes(models.Model):
    """ Связующая модель для рецептов и тегов."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'tag'),
                name='unique_recipe_tag'
            )
        ]


class BasicModelOfUserRecipeRelationship(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.user} {self.recipe}"


class Favorite(BasicModelOfUserRecipeRelationship):
    """ Любимые рецепты пользователей"""

    class Meta:
        default_related_name = "favorites"
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_user_recipe'
            )
        ]


class Basket(BasicModelOfUserRecipeRelationship):
    """ Корзина рецептов пользователей"""

    class Meta:
        default_related_name = "baskets"
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_basket_user_recipe'
            )
        ]
