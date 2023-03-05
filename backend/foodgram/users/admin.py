from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'first_name', 'last_name', 'email',
                    'is_active', 'is_superuser', 'get_quantity_of_followers',
                    'get_quantity_of_recipes')
    search_fields = ('username',)
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'

    def get_quantity_of_followers(self, obj):
        return obj.followers.count()

    def get_quantity_of_recipes(self, obj):
        return obj.recipes.count()

    get_quantity_of_followers.short_description = "Количество подписчиков"
    get_quantity_of_recipes.short_description = "Количество рецептов"
