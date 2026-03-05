"""Admin Django para todos os modelos."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'email', 'perfil', 'departamento', 'is_active']
    list_filter = ['perfil', 'is_active', 'is_staff', 'departamento']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'matricula']
    ordering = ['first_name', 'last_name']

    fieldsets = UserAdmin.fieldsets + (
        ('Informações IGC', {
            'fields': ('perfil', 'matricula', 'departamento', 'telefone', 'foto')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações IGC', {
            'fields': ('first_name', 'last_name', 'email', 'perfil', 'departamento')
        }),
    )
