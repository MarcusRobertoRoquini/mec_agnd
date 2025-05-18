from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'telefone', 'aprovado')}),
    )
    list_display = ('username', 'email', 'role', 'aprovado')

admin.site.register(User, CustomUserAdmin)
