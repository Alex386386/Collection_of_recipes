from django_filters import rest_framework
from rest_framework import filters
from recipes.models import Recipe, Tag


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'name'


class RecipeFilter(rest_framework.FilterSet):
    author = rest_framework.NumberFilter(field_name='author__id',
                                         lookup_expr='exact')
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = rest_framework.NumberFilter(method='filter_favorited',)
    is_in_shopping_cart = rest_framework.NumberFilter(
        method='filter_is_in_shopping_cart',)

    def filter_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated:
            if value == 1:
                return queryset.filter(
                    recipe_favorite__user=self.request.user)
            if value == 0:
                return queryset.exclude(
                    recipe_favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated:
            if value == 1:
                return queryset.filter(
                    recipe_shopping_cart__user=self.request.user)
            if value == 0:
                return queryset.exclude(
                    recipe_shopping_cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
