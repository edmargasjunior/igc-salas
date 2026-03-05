"""Admin de notificações."""
from django.contrib import admin
from .models import Notificacao


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ['destinatario', 'tipo', 'titulo', 'lida', 'email_enviado', 'criado_em']
    list_filter = ['tipo', 'lida', 'email_enviado', 'criado_em']
    search_fields = ['destinatario__first_name', 'destinatario__last_name', 'titulo']
    readonly_fields = ['criado_em', 'lida_em']
    raw_id_fields = ['destinatario', 'reserva']
    date_hierarchy = 'criado_em'
    list_per_page = 50

    actions = ['marcar_como_lida']

    def marcar_como_lida(self, request, queryset):
        from django.utils import timezone
        queryset.update(lida=True, lida_em=timezone.now())
        self.message_user(request, f'{queryset.count()} notificações marcadas como lidas.')
    marcar_como_lida.short_description = 'Marcar como lida'
