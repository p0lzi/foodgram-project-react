from django.core.validators import RegexValidator, MinValueValidator
from django.db import models

from users.models import User


class BaseModel(models.Model):
    """ Общая модель для классов рецепта, тегов и ингридиентов."""
    name = models.CharField('Название', max_length=200)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Ingredient(BaseModel):
    measurement_unit = models.CharField("Мера измерения", max_length=200)
    amount = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name} {self.measurement_unit}"


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
    name = models.CharField(max_length=200)
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
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name="Ингридиенты"
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagOfRecipes',
        verbose_name="Ингридиенты"
    )
    cooking_time = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def get_tags(self):
        """ Метод возвращает теги произведения. """
        return ', '.join([obj for obj in self.tags.all()])

    def get_ingredients(self):
        """ Метод возвращает теги произведения. """
        return ', '.join([obj for obj in self.ingredients.all()])

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """ Связующая модель для рецептов и ингредиентов."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)


class TagOfRecipes(models.Model):
    """ Связующая модель для рецептов и тегов."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, )
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


class Favorites(models.Model):
    """ Любимые рецепты пользователей"""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return self.recipe

    class Meta:
        verbose_name = "Любимый рецепт"
        verbose_name_plural = "Любимые рецепты"


class Basket(models.Model):
    """ Корзина рецептов пользователей"""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='basket')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return self.recipe

    class Meta:
        verbose_name = "Рецепт в корзине"
        verbose_name_plural = "Рецепты в корзине"
