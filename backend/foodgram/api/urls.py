from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from .views import (TagViewSet, RecipeViewSet,
                    FavoriteRecipeView, SubscribeView,
                    IngredientsViewSet, UserViewSet,
                    # CustomObtainAuthToken,
                    CustomDestroyToken, ShoppingCartView,
                    FavoriteRecipeView, SubscribeView,
                    DownloadShoppingCartView, SubscriptionsViewSet, SetPassword)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(r'users/subscriptions', SubscriptionsViewSet,
                   basename='subscription')

# router_v1.register(
#     'users', CustomUserViewSet, basename='users')
router_v1.register(
    r'tags', TagViewSet, basename='tag')
router_v1.register(
    r'recipes', RecipeViewSet, basename='recipe')
# router_v1.register(
#     r'recipes/(?P<recipe_id>\d+)/shopping_cart',
#     ShoppingCartView,
#     basename='shopping_cart')
# router_v1.register(
#     r'recipes/(?P<recipe_id>\d+)/favorites',
#     FavoriteRecipeView,
#     basename='favorite')
# router_v1.register(
#     r'users/(?P<user_id>\d+)/subscribe',
#     SubscribeView,
#     basename='subscribe')

router_v1.register(r'ingredients', IngredientsViewSet, basename='ingredient')


# Создаем отдельный кортеж для урлов регистрации и авторизации
# auth_patterns = (
#     [
#         path('logout/', CustomDestroyToken.as_view(), name='logout'),
#         path('login/', CustomObtainAuthToken.as_view(), name='login'),
#     ],
#     'auth'
# )

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    # path('users/set_password/', SetPassword.as_view(), name='set_password'),

    # path('auth/token/', include(auth_patterns)),
    path('download_shopping_cart/', DownloadShoppingCartView.as_view(),
         name='download_shopping_cart'),
    path('recipes/<int:recipe_id>/shopping_cart/',
         ShoppingCartView.as_view(), name='shopping_cart'),
    path('recipes/<int:recipe_id>/favorite/',
         FavoriteRecipeView.as_view(), name='favorite'),
    path('users/<int:user_id>/subscribe/',
         SubscribeView.as_view(), name='subscribe'),
]
