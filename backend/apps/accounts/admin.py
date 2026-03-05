"""Admin de contas e usuários."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'email', 'perfil', 'departamento', 'is_active']
    list_filter = ['perfil', 'is_active', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'matricula']
    list_editable = ['perfil', 'is_active']
    list_per_page = 30

    fieldsets = UserAdmin.fieldsets + (
        ('Dados IGC', {
            'fields': ('perfil', 'matricula', 'departamento', 'telefone', 'foto', 'slug', 'ativo')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Dados IGC', {
            'fields': ('first_name', 'last_name', 'email', 'perfil', 'departamento')
        }),
    )
    readonly_fields = ['slug', 'criado_em', 'atualizado_em']
