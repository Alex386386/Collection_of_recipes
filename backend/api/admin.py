from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (User, Tag, Ingredient, Recipe, Subscription,
                     ShoppingCart, Favorite)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )
    list_editable = ('slug',)
    search_fields = ('slug',)
    list_filter = ('name', 'color', 'slug',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    list_editable = ('measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ('count_favorite',)
    list_display = (
        'pk',
        'author',
        'name',
        'image',
        'is_favorited',
        'is_in_shopping_cart',
        'text',
        'cooking_time',
        'get_tags',
        'get_ingredients',
        'count_favorite',
    )
    list_editable = ('name',)
    search_fields = ('name', 'tags',)
    list_filter = ('name', 'author', 'tags',)
    empty_value_display = '-пусто-'

    def count_favorite(self, obj):
        return obj.recipe_favorite.all().count()


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )
    search_fields = ('user', 'recipe',)
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )
    search_fields = ('user', 'recipe',)
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'subscriber',
        'subscribed',
    )
    search_fields = ('user', 'author',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
