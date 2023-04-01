from django.urls import include, path
from rest_framework import routers

from .views import (TagViewSet, IngredientViewSet, UsersViewSet,
                    FavoriteViewSet, RecipeViewSet, SubscribeViewSet,
                    SubscriptionViewSet, ShoppingCartViewSet,
                    DownloadShoppingCartViewSet)

v1_router = routers.DefaultRouter()
v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')
v1_router.register('recipes/download_shopping_cart',
                   DownloadShoppingCartViewSet, basename='download')
v1_router.register('recipes', RecipeViewSet, basename='recipes')
v1_router.register('users/subscriptions', SubscriptionViewSet,
                   basename='subscriptions')
v1_router.register(r'users/(?P<user_id>\d+)/subscribe',
                   SubscribeViewSet, basename='subscribe')
v1_router.register(r'recipes/(?P<recipe_id>\d+)/favorite',
                   FavoriteViewSet, basename='favorite')
v1_router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
                   ShoppingCartViewSet, basename='shopping_cart')
v1_router.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path(r'auth/', include('djoser.urls.authtoken')),
    path('', include(v1_router.urls)),
]
