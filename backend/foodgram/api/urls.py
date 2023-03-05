from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientsViewSet, RecipeViewSet, SubscribeView,
                    SubscriptionsViewSet, TagViewSet)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(r'users/subscriptions', SubscriptionsViewSet,
                   basename='subscription')
router_v1.register(
    r'tags', TagViewSet, basename='tag')
router_v1.register(
    r'recipes', RecipeViewSet, basename='recipe')

router_v1.register(r'ingredients', IngredientsViewSet, basename='ingredient')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('users/<int:user_id>/subscribe/',
         SubscribeView.as_view(), name='subscribe'),
]
