from django.contrib import admin

from .models import Recipe, Tag, Ingredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """ Класс для управления рецептами в админке. """

    list_display = ('name', 'author', 'get_tags', 'get_ingredients')
    list_filter = ('name', 'author')
    search_fields = ('name', 'author', )
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """ Класс для управления рецептами в админке. """

    list_display = ('name', 'color')
    list_filter = ('name', 'color', 'slug')
    search_fields = ('name', 'slug', )
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """ Класс для управления рецептами в админке. """

    list_display = ('name', 'measurement_unit', 'amount')
    list_filter = ('name', 'measurement_unit', )
    search_fields = ('name', 'measurement_unit', )
    empty_value_display = '-пусто-'
