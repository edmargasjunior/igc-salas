"""Admin para reservas."""
from django.contrib import admin
from .models import Reserva, LogReserva


class LogInline(admin.TabularInline):
    model = LogReserva
    extra = 0
    readonly_fields = ['acao', 'descricao', 'usuario', 'criado_em']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['pk', 'sala', 'solicitante', 'data_inicio', 'hora_inicio', 'hora_fim', 'status', 'tipo']
    list_filter = ['status', 'tipo', 'data_inicio', 'sala__andar__predio']
    search_fields = ['solicitante__first_name', 'sala__nome', 'motivo']
    date_hierarchy = 'data_inicio'
    readonly_fields = ['aprovado_por', 'data_aprovacao', 'criado_em', 'atualizado_em']
    inlines = [LogInline]
    actions = ['aprovar_selecionadas']

    def aprovar_selecionadas(self, request, queryset):
        from .services import ReservaService
        s = ReservaService()
        count = 0
        for r in queryset.filter(status='pendente'):
            try:
                s.aprovar_reserva(r, request.user, request)
                count += 1
            except Exception:
                pass
        self.message_user(request, f'{count} reserva(s) aprovada(s).')
    aprovar_selecionadas.short_description = 'Aprovar reservas selecionadas'


@admin.register(LogReserva)
class LogReservaAdmin(admin.ModelAdmin):
    list_display = ['reserva', 'acao', 'usuario', 'criado_em']
    list_filter = ['acao', 'criado_em']
    readonly_fields = ['reserva', 'usuario', 'acao', 'descricao', 'dados_anteriores', 'ip_address', 'criado_em']
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
