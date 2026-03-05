"""Views do módulo acadêmico: Professor, Turma, Disciplina."""
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q, Count
from django.utils import timezone

from .models import Professor, Turma, Disciplina


class ProfessorDetalheView(View):
    """Página pública de agenda de um professor."""
    template_name = 'academico/professor.html'

    def get(self, request, slug):
        professor = get_object_or_404(Professor, slug=slug, ativo=True)
        hoje = timezone.now().date()
        from datetime import timedelta
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        fim_semana = inicio_semana + timedelta(days=6)

        from apps.reservas.models import Reserva
        reservas_semana = Reserva.objects.filter(
            turma__professor=professor,
            data_inicio__range=[inicio_semana, fim_semana],
            status=Reserva.Status.APROVADA
        ).select_related('sala__andar__predio', 'turma__disciplina').order_by('data_inicio', 'hora_inicio')

        turmas_ativas = Turma.objects.filter(
            professor=professor, ativo=True, ano=hoje.year
        ).select_related('disciplina').order_by('disciplina__nome')

        return render(request, self.template_name, {
            'professor': professor,
            'reservas_semana': reservas_semana,
            'turmas_ativas': turmas_ativas,
            'semana_inicio': inicio_semana,
            'semana_fim': fim_semana,
        })


class TurmaDetalheView(View):
    """Página pública de detalhe de uma turma."""
    template_name = 'academico/turma.html'

    def get(self, request, slug):
        turma = get_object_or_404(Turma, slug=slug, ativo=True)
        hoje = timezone.now().date()

        from apps.reservas.models import Reserva
        reservas = Reserva.objects.filter(
            turma=turma,
            status=Reserva.Status.APROVADA,
            data_inicio__gte=hoje
        ).select_related('sala__andar__predio').order_by('data_inicio', 'hora_inicio')[:20]

        return render(request, self.template_name, {
            'turma': turma,
            'reservas': reservas,
        })


class DisciplinaDetalheView(View):
    template_name = 'academico/disciplina.html'

    def get(self, request, slug):
        disciplina = get_object_or_404(Disciplina, slug=slug, ativo=True)
        turmas = Turma.objects.filter(disciplina=disciplina, ativo=True).select_related('professor__usuario')
        return render(request, 'academico/disciplina.html', {
            'disciplina': disciplina,
            'turmas': turmas,
        })


class ProfessorListaView(View):
    """Lista de professores para gestão (autenticado)."""
    template_name = 'academico/professores_lista.html'

    @method_decorator(login_required)
    def get(self, request):
        q = request.GET.get('q', '')
        professores = Professor.objects.filter(ativo=True).select_related('usuario')
        if q:
            professores = professores.filter(
                Q(usuario__first_name__icontains=q) |
                Q(usuario__last_name__icontains=q) |
                Q(siape__icontains=q)
            )
        professores = professores.annotate(
            total_turmas=Count('turmas', filter=Q(turmas__ativo=True))
        ).order_by('usuario__first_name')
        return render(request, self.template_name, {
            'professores': professores, 'q': q
        })


class TurmaListaView(View):
    """Lista de turmas para gestão (autenticado)."""
    template_name = 'academico/turmas_lista.html'

    @method_decorator(login_required)
    def get(self, request):
        ano = request.GET.get('ano', timezone.now().year)
        q = request.GET.get('q', '')
        turmas = Turma.objects.filter(ativo=True, ano=ano).select_related(
            'disciplina', 'professor__usuario'
        )
        if q:
            turmas = turmas.filter(
                Q(disciplina__nome__icontains=q) |
                Q(disciplina__codigo__icontains=q) |
                Q(codigo__icontains=q)
            )
        turmas = turmas.order_by('disciplina__nome', 'codigo')
        return render(request, self.template_name, {
            'turmas': turmas, 'ano': ano, 'q': q
        })
