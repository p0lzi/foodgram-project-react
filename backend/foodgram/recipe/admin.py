from django.contrib import admin

from .models import Ingredient, IngredientInRecipe, Recipe, Tag, TagOfRecipes


class IngredientInline(admin.TabularInline):
    model = IngredientInRecipe


class TagsInline(admin.TabularInline):
    model = TagOfRecipes
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """ Класс для управления рецептами в админке. """
    inlines = [IngredientInline, TagsInline]

    list_display = ('name', 'author', 'get_tags', 'get_quantity_in_favorites')
    list_filter = ('name', 'author', 'tags__name')
    search_fields = ('name', 'author')
    empty_value_display = '-пусто-'

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    def get_quantity_in_favorites(self, obj):
        return obj.favorite_set.count()

    get_tags.short_description = 'Теги'
    get_quantity_in_favorites.short_description = 'Количество в избранном'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """ Класс для управления рецептами в админке. """
    inlines = [TagsInline]

    list_display = ('name', 'color')
    list_filter = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """ Класс для управления рецептами в админке. """

    list_display = ('name', 'measurement_unit')
    list_filter = ('name', 'measurement_unit',)
    search_fields = ('name', 'measurement_unit',)
    empty_value_display = '-пусто-'
