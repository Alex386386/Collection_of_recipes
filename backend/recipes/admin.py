from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User, Subscription


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
