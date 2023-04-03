from collections import defaultdict

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)
from rest_framework.response import Response

from .filters import RecipeFilter, IngredientSearchFilter
from recipes.models import Tag, Ingredient, Recipe, ShoppingCart, Favorite
from users.models import User, Subscription
from .pagination import CustomPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (DownloadShoppingCartSerializer, TagSerializer,
                          IngredientSerializer, RecipeSerializer,
                          SubscriptionSerializer, RecipeSerializerGet,
                          FavoriteSerializer, ShoppingCartSerializer,)
from .utils import (CreateDestroyViewSet,
                    FavoriteShoppingViewSet,
                    TagIngredientViewSet)


class UsersViewSet(UserViewSet):
    """Взаимодействие с моделью пользователей."""
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination


class TagViewSet(TagIngredientViewSet):
    """Получения тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(TagIngredientViewSet):
    """Получение списка ингредиентов, фильтрация по полю name."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Получение и создание рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return RecipeSerializerGet
        return RecipeSerializer


class SubscribeViewSet(CreateDestroyViewSet):
    """Создание и удаление подписок."""
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def get_user(self):
        return get_object_or_404(User, pk=self.kwargs.get('user_id'))

    def perform_create(self, serializer):
        serializer.save(
            subscriber=self.request.user,
            subscribed=self.get_user()
        )

    def delete(self, request, user_id):
        subscription = get_object_or_404(
            Subscription,
            subscriber=request.user,
            subscribed=self.get_user(),
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['subscribed_id'] = int(self.kwargs.get('user_id'))
        return context


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """Вывод всех подписок пользователя."""
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        user = get_object_or_404(User, id=request.user.id)
        queryset = user.subscriber.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionSerializer(page,
                                                many=True,
                                                context={'request': request})
            return self.get_paginated_response(serializer.data)


class FavoriteViewSet(FavoriteShoppingViewSet):
    """Добавление и удаление рецепта в избранное."""
    serializer_class = FavoriteSerializer
    model = Favorite


class ShoppingCartViewSet(FavoriteShoppingViewSet):
    """Добавление и удаление рецепта в список покупок."""
    serializer_class = ShoppingCartSerializer
    model = ShoppingCart


class DownloadShoppingCartViewSet(viewsets.ReadOnlyModelViewSet):
    """Скачать список продуктов."""

    def list(self, request):
        queryset = ShoppingCart.objects.filter(
            user=request.user).prefetch_related('recipe')
        serializer = DownloadShoppingCartSerializer(
            queryset, many=True, context={'request': request})
        data = serializer.data
        result = defaultdict(int)
        for item in data:
            for ingredient in item['ingredients']:
                result[ingredient['name'], ingredient[
                    'measurement_unit']] += ingredient['amount']
        response_data = ''
        for key, value in result.items():
            response_data += f'{key[0]}({key[1]})-{value}\n'
        response = HttpResponse(response_data, content_type='text/plain')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response
