from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'first_name', 'last_name', 'email',
                    'is_active', 'is_superuser')
    search_fields = ('username',)
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'
