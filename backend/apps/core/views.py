"""
Views do Core - Tela pública e Dashboard
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.db.models import Q, Count
from datetime import date, timedelta


class IndexView(View):
    """Tela inicial pública - Motor de busca de salas."""
    template_name = 'public/index.html'

    def get(self, request):
        from apps.estrutura.models import Sala
        from apps.academico.models import Professor
        # Estatísticas públicas
        total_salas = Sala.objects.filter(ativo=True).count()
        total_labs = Sala.objects.filter(ativo=True, tipo='laboratorio').count()
        total_professores = Professor.objects.filter(ativo=True).count()

        return render(request, self.template_name, {
            'total_salas': total_salas,
            'total_labs': total_labs,
            'total_professores': total_professores,
        })


class DashboardView(View):
    """Dashboard principal para usuários autenticados."""
    template_name = 'dashboard/index.html'

    @method_decorator(login_required)
    def get(self, request):
        from apps.reservas.models import Reserva
        from apps.estrutura.models import Sala
        from apps.notificacoes.models import Notificacao

        hoje = date.today()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        fim_semana = inicio_semana + timedelta(days=6)

        # Estatísticas gerais
        stats = {
            'total_salas': Sala.objects.filter(ativo=True).count(),
            'reservas_hoje': Reserva.objects.filter(
                data_inicio=hoje, status=Reserva.Status.APROVADA
            ).count(),
            'reservas_semana': Reserva.objects.filter(
                data_inicio__range=[inicio_semana, fim_semana],
                status=Reserva.Status.APROVADA
            ).count(),
            'pendentes': Reserva.objects.filter(status=Reserva.Status.PENDENTE).count(),
        }

        # Reservas recentes do usuário
        minhas_reservas = Reserva.objects.filter(
            solicitante=request.user
        ).select_related('sala', 'turma__disciplina').order_by('-criado_em')[:5]

        # Notificações não lidas
        notificacoes = Notificacao.objects.filter(
            destinatario=request.user, lida=False
        ).order_by('-criado_em')[:5]

        # Reservas de hoje para admins
        reservas_hoje = []
        if request.user.is_responsavel:
            reservas_hoje = Reserva.objects.filter(
                data_inicio=hoje
            ).select_related(
                'sala', 'solicitante', 'turma__disciplina'
            ).order_by('hora_inicio')[:10]

        # Pendentes para aprovação (admins)
        pendentes_aprovacao = []
        if request.user.pode_aprovar_reservas():
            pendentes_aprovacao = Reserva.objects.filter(
                status=Reserva.Status.PENDENTE
            ).select_related(
                'sala', 'solicitante', 'turma__disciplina'
            ).order_by('criado_em')[:10]

        return render(request, self.template_name, {
            'stats': stats,
            'minhas_reservas': minhas_reservas,
            'notificacoes': notificacoes,
            'reservas_hoje': reservas_hoje,
            'pendentes_aprovacao': pendentes_aprovacao,
        })


class DashboardOcupacaoView(View):
    """Dashboard de ocupação de salas com gráficos."""
    template_name = 'dashboard/ocupacao.html'

    @method_decorator(login_required)
    def get(self, request):
        from apps.estrutura.models import Sala
        from apps.reservas.models import Reserva

        hoje = date.today()
        inicio = hoje - timedelta(days=30)

        # Ocupação por sala nos últimos 30 dias
        ocupacao_salas = Sala.objects.filter(ativo=True).annotate(
            total_reservas=Count(
                'reservas',
                filter=Q(
                    reservas__status=Reserva.Status.APROVADA,
                    reservas__data_inicio__gte=inicio
                )
            )
        ).order_by('-total_reservas')[:15]

        return render(request, self.template_name, {
            'ocupacao_salas': ocupacao_salas,
            'periodo': f"{inicio.strftime('%d/%m/%Y')} - {hoje.strftime('%d/%m/%Y')}",
        })
