from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (DownloadShoppingCartView, FavoriteRecipeView,
                    IngredientsViewSet, RecipeViewSet, ShoppingCartView,
                    SubscribeView, SubscriptionsViewSet, TagViewSet)

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
    path('recipes/download_shopping_cart/', DownloadShoppingCartView.as_view(),
         name='download_shopping_cart'),
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),

    path('recipes/<int:recipe_id>/shopping_cart/',
         ShoppingCartView.as_view(), name='shopping_cart'),
    path('recipes/<int:recipe_id>/favorite/',
         FavoriteRecipeView.as_view(), name='favorite'),
    path('users/<int:user_id>/subscribe/',
         SubscribeView.as_view(), name='subscribe'),
]
