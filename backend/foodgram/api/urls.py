from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from .views import (TagViewSet, RecipeViewSet, DownloadShoppingCartViewSet,
                    FavoriteRecipeViewSet, SubscriptionsViewSet,
                    IngredientsViewSet, UserViewSet, CustomObtainAuthToken,
                    CustomDestroyToken)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register(r'tags', TagViewSet, basename='tag')
router_v1.register(r'recipes', RecipeViewSet, basename='recipe')
router_v1.register(r'recipes/download_shopping_cart',
                   DownloadShoppingCartViewSet, basename='shopcart')
router_v1.register(r'recipes/(?P<recipe_id>\d+)/favorites',
                   FavoriteRecipeViewSet, basename='favorite')
router_v1.register(r'users/subscriptions',
                   SubscriptionsViewSet, basename='subscriptions')

router_v1.register(r'ingredients', IngredientsViewSet, basename='ingredient')

# router_v1.register(
#     r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
# )
# router_v1.register(
#     r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     CommentViewSet, basename='comments'
# )


urlpatterns = [
    path('', include(router_v1.urls)),
    # path('auth/token/login/', ObtainUserToken.as_view(), name='token'),
    path('auth/token/login/', CustomObtainAuthToken.as_view(), name='token'),
    path('auth/token/logout/', CustomDestroyToken.as_view(), name='logout')
]
