from django_filters import rest_framework as filters
from recipe.models import Recipe


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    """ Фильтр для фильтрации по строке в фильтре. """
    pass


class RecipeFilter(filters.FilterSet):
    """ Фильтр для произведений. """
    is_favorited = filters.BooleanFilter(method="filter_is_set")
    is_in_shopping_cart = filters.BooleanFilter(method="filter_is_set")
    tags = CharFilterInFilter(field_name='tags__slug', lookup_expr='in')
    author = filters.NumberFilter(field_name="author__pk")

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filter_is_set(self, queryset, name, value):
        names = {
            "is_favorited": "is_favorited__user",
            "is_in_shopping_cart": "in_basket__user"
        }
        if value:
            return queryset.filter(**{names[name]: self.request.user})
        return queryset.exclude(**{names[name]: self.request.user})
