from django.shortcuts import get_object_or_404
from rest_framework.mixins import DestroyModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from recipes.models import Recipe
from rest_framework import status, viewsets
from rest_framework.response import Response


class CreateDestroyViewSet(CreateModelMixin, DestroyModelMixin,
                           GenericViewSet):
    pass


class TagIngredientViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None


class FavoriteShoppingViewSet(CreateDestroyViewSet):
    permission_classes = (IsAuthenticated,)
    model = None

    def get_recipe(self):
        return get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            recipe=self.get_recipe(), )

    def delete(self, request, recipe_id):
        favorite = get_object_or_404(
            self.model,
            user=self.request.user,
            recipe=self.get_recipe(),
        )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recipe_id'] = int(self.kwargs.get('recipe_id'))
        return context


def get_ingredients_dict(ingredients_data):
    ingredients_dict = {}
    for ingredient in ingredients_data:
        ingredient_id = ingredient.get('ingredient').get('id')
        amount = ingredient.get('amount')
        if ingredient_id in ingredients_dict:
            ingredients_dict[ingredient_id] += amount
        else:
            ingredients_dict[ingredient_id] = amount
    return ingredients_dict
