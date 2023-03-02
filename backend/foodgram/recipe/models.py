from django.core.validators import RegexValidator, MinValueValidator
from django.db import models

from users.models import User


class BaseModel(models.Model):
    """ Общая модель для классов рецепта, тегов и ингридиентов."""
    name = models.CharField('Название', max_length=200, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Ingredient(BaseModel):
    measurement_unit = models.CharField("Мера измерения", max_length=200)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"


class Tag(BaseModel):
    color = models.CharField(max_length=7,
                             validators=[
                                 RegexValidator(regex='^#[0-9A-F]{6,6}$')])
    slug = models.SlugField('URL', unique=True, max_length=200,
                            validators=[
                                RegexValidator(regex='[-a-zA-Z0-9_]+')])

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


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
        verbose_name="Ингридиенты"
    )
    cooking_time = models.IntegerField(validators=[MinValueValidator(1)])
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def get_tags(self):
        """ Метод возвращает теги произведения. """
        return ', '.join([obj for obj in self.tags.all()])

    def get_ingredients(self):
        """ Метод возвращает теги произведения. """
        return ', '.join([obj for obj in self.ingredients.all()])


class IngredientInRecipe(models.Model):
    """ Связующая модель для рецептов и ингредиентов."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name="ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField(validators=[MinValueValidator(1)])


class TagOfRecipes(models.Model):
    """ Связующая модель для рецептов и тегов."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


class Favorites(models.Model):
    """ Любимые рецепты пользователей"""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='is_favorited')

    def __str__(self):
        return self.recipe.name

    class Meta:
        verbose_name = "Любимый рецепт"
        verbose_name_plural = "Любимые рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe'
            )
        ]


class Basket(models.Model):
    """ Корзина рецептов пользователей"""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='basket')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='in_basket')

    def __str__(self):
        return self.recipe.name

    class Meta:
        verbose_name = "Рецепт в корзине"
        verbose_name_plural = "Рецепты в корзине"
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe'
            )
        ]
