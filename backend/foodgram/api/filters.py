from django_filters import rest_framework as filters
from recipe.models import Recipe


# class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
#     """ Фильтр для фильтрации по строке в фильтре. """
#     pass
#
#
# class TitleFilter(filters.FilterSet):
#     """ Фильтр для произведений. """
#
#     genre = CharFilterInFilter(field_name='genre__slug', lookup_expr='in')
#     year = filters.NumberFilter()
#     name = filters.CharFilter(lookup_expr='icontains')
#     category = CharFilterInFilter(field_name='category__slug')
#
#     class Meta:
#         model = Title
#         fields = ('genre', 'year', 'name', 'category')
