"""Admin de reservas com painel completo."""
from django.contrib import admin
from django.utils.html import format_html
from .models import Reserva, LogReserva


class LogReservaInline(admin.TabularInline):
    model = LogReserva
    extra = 0
    readonly_fields = ['usuario', 'acao', 'descricao', 'ip_address', 'criado_em']
    can_delete = False


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['id', 'sala', 'solicitante', 'data_inicio', 'hora_inicio',
                    'hora_fim', 'tipo', 'status_colorido', 'turma']
    list_filter = ['status', 'tipo', 'data_inicio', 'sala__andar__predio']
    search_fields = ['sala__nome', 'sala__codigo', 'solicitante__first_name',
                     'solicitante__last_name', 'motivo']
    raw_id_fields = ['sala', 'solicitante', 'turma', 'aprovado_por']
    date_hierarchy = 'data_inicio'
    readonly_fields = ['criado_em', 'atualizado_em', 'data_aprovacao']
    inlines = [LogReservaInline]
    list_per_page = 30

    fieldsets = (
        ('Reserva', {'fields': ('sala', 'solicitante', 'turma', 'tipo', 'status')}),
        ('Horário', {'fields': ('data_inicio', 'data_fim', 'hora_inicio', 'hora_fim', 'recorrencia', 'dia_semana')}),
        ('Aprovação', {'fields': ('aprovado_por', 'data_aprovacao', 'motivo_rejeicao', 'motivo_override')}),
        ('Detalhes', {'fields': ('motivo', 'observacoes', 'criado_em', 'atualizado_em')}),
    )

    def status_colorido(self, obj):
        cores = {
            'pendente': '#f59e0b', 'aprovada': '#10b981', 'rejeitada': '#ef4444',
            'cancelada': '#94a3b8', 'substituida': '#8b5cf6', 'expirada': '#64748b',
        }
        cor = cores.get(obj.status, '#64748b')
        return format_html(
            '<span style="color:{};font-weight:600">● {}</span>',
            cor, obj.get_status_display()
        )
    status_colorido.short_description = 'Status'


@admin.register(LogReserva)
class LogReservaAdmin(admin.ModelAdmin):
    list_display = ['criado_em', 'reserva', 'usuario', 'acao', 'ip_address']
    list_filter = ['acao', 'criado_em']
    search_fields = ['reserva__id', 'usuario__first_name', 'descricao']
    readonly_fields = ['reserva', 'usuario', 'acao', 'descricao', 'dados_anteriores', 'ip_address', 'criado_em']
    date_hierarchy = 'criado_em'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
