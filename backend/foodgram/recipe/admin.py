from django.contrib import admin

from .models import Recipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """ Класс для управления рецептами в админке. """

    list_display = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author', )
    empty_value_display = '-пусто-'
