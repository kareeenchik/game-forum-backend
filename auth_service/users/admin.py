from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class MyUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'nickname', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('role', 'nickname')}),
    )