"""Views do módulo acadêmico: Professor, Turma, Disciplina — com CRUD completo."""
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib import messages

from .models import Professor, Turma, Disciplina


# ──────────────────────────── VIEWS PÚBLICAS ────────────────────────────

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


# ──────────────────────────── VIEWS ADMIN PROFESSORES ────────────────────────────

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


class ProfessorCriarView(View):
    template_name = 'academico/professor_form.html'

    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_responsavel:
            return redirect('dashboard')
        return render(request, self.template_name, {
            'professor': None,
            'titulacao_choices': Professor.Titulacao.choices,
        })

    @method_decorator(login_required)
    def post(self, request):
        if not request.user.is_responsavel:
            return redirect('dashboard')
        try:
            from apps.accounts.models import Usuario
            user = Usuario(
                first_name=request.POST.get('first_name', '').strip(),
                last_name=request.POST.get('last_name', '').strip(),
                email=request.POST.get('email', '').strip(),
                username=request.POST.get('email', '').split('@')[0],
                perfil='professor',
                departamento=request.POST.get('departamento', ''),
                telefone=request.POST.get('telefone', ''),
            )
            user.set_password(request.POST.get('password', 'IGC@12345'))
            user.save()

            professor = Professor(
                usuario=user,
                siape=request.POST.get('siape', '').strip(),
                titulacao=request.POST.get('titulacao', Professor.Titulacao.DOUTOR),
                area_atuacao=request.POST.get('area_atuacao', ''),
                lattes=request.POST.get('lattes', ''),
            )
            professor.save()
            messages.success(request, f'Professor {professor.nome} cadastrado com sucesso!')
            return redirect('professores_lista')
        except Exception as e:
            messages.error(request, f'Erro ao cadastrar professor: {e}')
            return redirect('professores_lista')


class ProfessorEditarView(View):
    template_name = 'academico/professor_form.html'

    @method_decorator(login_required)
    def get(self, request, pk):
        if not request.user.is_responsavel:
            return redirect('dashboard')
        professor = get_object_or_404(Professor, pk=pk)
        return render(request, self.template_name, {
            'professor': professor,
            'titulacao_choices': Professor.Titulacao.choices,
        })

    @method_decorator(login_required)
    def post(self, request, pk):
        if not request.user.is_responsavel:
            return redirect('dashboard')
        professor = get_object_or_404(Professor, pk=pk)
        try:
            professor.siape = request.POST.get('siape', professor.siape).strip()
            professor.titulacao = request.POST.get('titulacao', professor.titulacao)
            professor.area_atuacao = request.POST.get('area_atuacao', professor.area_atuacao)
            professor.lattes = request.POST.get('lattes', professor.lattes)
            professor.save()
            user = professor.usuario
            user.departamento = request.POST.get('departamento', user.departamento)
            user.telefone = request.POST.get('telefone', user.telefone)
            user.save()
            messages.success(request, f'Professor {professor.nome} atualizado.')
        except Exception as e:
            messages.error(request, f'Erro: {e}')
        return redirect('professores_lista')


# ──────────────────────────── VIEWS ADMIN TURMAS ────────────────────────────

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


class TurmaCriarView(View):
    template_name = 'academico/turma_form.html'

    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_responsavel:
            return redirect('dashboard')
        disciplinas = Disciplina.objects.filter(ativo=True).order_by('nome')
        professores = Professor.objects.filter(ativo=True).select_related('usuario').order_by('usuario__first_name')
        return render(request, self.template_name, {
            'turma': None,
            'disciplinas': disciplinas,
            'professores': professores,
            'ano_atual': timezone.now().year,
        })

    @method_decorator(login_required)
    def post(self, request):
        if not request.user.is_responsavel:
            return redirect('dashboard')
        try:
            disciplina_id = request.POST.get('disciplina_id')
            professor_id = request.POST.get('professor_id')
            disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
            professor = Professor.objects.filter(pk=professor_id).first() if professor_id else None
            turma = Turma(
                disciplina=disciplina,
                professor=professor,
                codigo=request.POST.get('codigo', '').strip(),
                ano=int(request.POST.get('ano', timezone.now().year)),
                semestre=request.POST.get('semestre', '1'),
                vagas=int(request.POST.get('vagas', 40)),
                matriculados=int(request.POST.get('matriculados', 0)),
            )
            turma.save()
            messages.success(request, f'Turma {turma} criada com sucesso!')
            return redirect('turmas_lista')
        except Exception as e:
            messages.error(request, f'Erro ao criar turma: {e}')
            return redirect('turmas_lista')


class TurmaEditarView(View):
    template_name = 'academico/turma_form.html'

    @method_decorator(login_required)
    def get(self, request, pk):
        if not request.user.is_responsavel:
            return redirect('dashboard')
        turma = get_object_or_404(Turma, pk=pk)
        disciplinas = Disciplina.objects.filter(ativo=True).order_by('nome')
        professores = Professor.objects.filter(ativo=True).select_related('usuario').order_by('usuario__first_name')
        return render(request, self.template_name, {
            'turma': turma,
            'disciplinas': disciplinas,
            'professores': professores,
            'ano_atual': turma.ano,
        })

    @method_decorator(login_required)
    def post(self, request, pk):
        if not request.user.is_responsavel:
            return redirect('dashboard')
        turma = get_object_or_404(Turma, pk=pk)
        try:
            disciplina_id = request.POST.get('disciplina_id')
            professor_id = request.POST.get('professor_id')
            turma.disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
            turma.professor = Professor.objects.filter(pk=professor_id).first() if professor_id else None
            turma.codigo = request.POST.get('codigo', turma.codigo).strip()
            turma.ano = int(request.POST.get('ano', turma.ano))
            turma.semestre = request.POST.get('semestre', turma.semestre)
            turma.vagas = int(request.POST.get('vagas', turma.vagas))
            turma.matriculados = int(request.POST.get('matriculados', turma.matriculados))
            turma.save()
            messages.success(request, f'Turma {turma} atualizada.')
        except Exception as e:
            messages.error(request, f'Erro: {e}')
        return redirect('turmas_lista')
