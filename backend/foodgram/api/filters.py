from django_filters import rest_framework as filters
from recipe.models import Recipe


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    """ Фильтр для фильтрации по строке в фильтре. """
    pass


class RecipeFilter(filters.FilterSet):
    """ Фильтр для произведений. """
    is_favorited = filters.BooleanFilter()
    is_in_shopping_cart = filters.BooleanFilter()
    author = filters.NumberFilter()
    tags = CharFilterInFilter(field_name='tags__slug', lookup_expr='in')

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')
