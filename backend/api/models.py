from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    first_name = models.CharField(
        max_length=150,
        verbose_name='Firstname',
        null=True)
    last_name = models.CharField(
        max_length=150,
        verbose_name='Lastname',
        null=True)
    username = models.CharField(
        max_length=150,
        verbose_name='Username',
        unique=True
    )
    email = models.EmailField(
        verbose_name='Email',
        unique=True,
        max_length=254
    )
    is_subscribed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.username}'


class Tag(models.Model):
    name = models.CharField(
        max_length=30,
        verbose_name='Тэг',
    )
    color = models.CharField(max_length=7)
    slug = models.SlugField(
        unique=True,
        max_length=20,
        verbose_name='slug-значение тэга'
    )

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=60,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=10,
        verbose_name='Единица измерения ингредиента'
    )

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, through='RecipeTag',)
    author = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',)
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        upload_to='images/',
        null=True,
        default=None
        )
    text = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ('-id',)

    def get_tags(self):
        return "\n".join([p.slug for p in self.tags.all()])

    def get_ingredients(self):
        return "\n".join([p.name for p in self.ingredients.all()])

    def __str__(self):
        return f'{self.name} {self.author}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipeingredient',
        verbose_name='рецепт')
    ingredient = models.ForeignKey(
        Ingredient,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='ingredient',
        verbose_name='ингредиент')
    amount = models.PositiveSmallIntegerField(
        help_text='Введите количество ингредиента',
        default=0,
    )

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipetag',
        verbose_name='рецепт')
    tag = models.ForeignKey(
        Tag,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='tag',
        verbose_name='тэг')

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )
    subscribed = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed',
        verbose_name='Автор на которого подписываются',
    )

    def __str__(self):
        return f'{self.subscriber} {self.subscribed}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_favorite',
        verbose_name='Юзер для рецепта',
    )
    recipe = models.ForeignKey(
        Recipe,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='recipe_favorite',
        verbose_name='Рецепт избран',
        help_text='Рецепт в избранном'
    )

    def __str__(self):
        return f'{self.user} {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_shopping_cart',
        verbose_name='Юзер для рецепта',
    )
    recipe = models.ForeignKey(
        Recipe,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='recipe_shopping_cart',
        verbose_name='Список покупок',
        help_text='список покупок для рецепта'
    )

    def __str__(self):
        return f'{self.user} {self.recipe}'
