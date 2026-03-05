"""
API de Busca em Tempo Real (Autocomplete)
Retorna resultados de salas, laboratórios, professores, turmas e disciplinas.
"""
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class BuscaGlobalAPIView(APIView):
    """
    Endpoint de busca global para a tela pública.
    GET /api/v1/busca/?q=termo&tipo=sala|professor|turma|disciplina
    """
    permission_classes = [AllowAny]

    def get(self, request):
        q = request.GET.get('q', '').strip()
        tipo = request.GET.get('tipo', 'todos')

        if len(q) < 2:
            return Response({'resultados': [], 'total': 0})

        resultados = []

        if tipo in ['todos', 'sala', 'laboratorio']:
            resultados += self._buscar_salas(q, tipo)

        if tipo in ['todos', 'professor']:
            resultados += self._buscar_professores(q)

        if tipo in ['todos', 'turma']:
            resultados += self._buscar_turmas(q)

        if tipo in ['todos', 'disciplina']:
            resultados += self._buscar_disciplinas(q)

        return Response({
            'resultados': resultados[:20],
            'total': len(resultados),
            'query': q,
        })

    def _buscar_salas(self, q, tipo='todos'):
        from apps.estrutura.models import Sala
        qs = Sala.objects.filter(ativo=True).filter(
            Q(nome__icontains=q) |
            Q(codigo__icontains=q) |
            Q(descricao__icontains=q) |
            Q(andar__predio__nome__icontains=q)
        ).select_related('andar__predio')

        if tipo == 'laboratorio':
            qs = qs.filter(tipo='laboratorio')

        resultados = []
        for sala in qs[:10]:
            resultados.append({
                'tipo': 'sala',
                'subtipo': sala.tipo,
                'id': sala.pk,
                'titulo': sala.nome,
                'subtitulo': f"{sala.andar.predio.nome} — {str(sala.andar)}",
                'capacidade': sala.capacidade,
                'url': sala.get_absolute_url(),
                'slug': sala.slug,
                'icone': 'flask' if sala.is_laboratorio else 'door-open',
                'badge': sala.get_tipo_display(),
            })
        return resultados

    def _buscar_professores(self, q):
        from apps.academico.models import Professor
        qs = Professor.objects.filter(ativo=True).filter(
            Q(usuario__first_name__icontains=q) |
            Q(usuario__last_name__icontains=q) |
            Q(siape__icontains=q) |
            Q(area_atuacao__icontains=q)
        ).select_related('usuario')

        resultados = []
        for prof in qs[:8]:
            resultados.append({
                'tipo': 'professor',
                'id': prof.pk,
                'titulo': f"Prof. {prof.usuario.nome_completo}",
                'subtitulo': prof.area_atuacao or prof.get_titulacao_display(),
                'url': prof.get_absolute_url(),
                'slug': prof.slug,
                'icone': 'chalkboard-teacher',
                'badge': prof.get_titulacao_display(),
            })
        return resultados

    def _buscar_turmas(self, q):
        from apps.academico.models import Turma
        from django.utils import timezone
        ano_atual = timezone.now().year

        qs = Turma.objects.filter(ativo=True).filter(
            Q(codigo__icontains=q) |
            Q(disciplina__nome__icontains=q) |
            Q(disciplina__codigo__icontains=q) |
            Q(professor__usuario__first_name__icontains=q) |
            Q(professor__usuario__last_name__icontains=q)
        ).filter(ano=ano_atual).select_related(
            'disciplina', 'professor__usuario'
        )[:8]

        resultados = []
        for turma in qs:
            resultados.append({
                'tipo': 'turma',
                'id': turma.pk,
                'titulo': str(turma.disciplina),
                'subtitulo': f"Turma {turma.codigo} — {turma.periodo}",
                'professor': str(turma.professor) if turma.professor else '',
                'url': turma.get_absolute_url(),
                'slug': turma.slug,
                'icone': 'users',
                'badge': turma.periodo,
            })
        return resultados

    def _buscar_disciplinas(self, q):
        from apps.academico.models import Disciplina
        qs = Disciplina.objects.filter(ativo=True).filter(
            Q(nome__icontains=q) |
            Q(codigo__icontains=q) |
            Q(departamento__icontains=q)
        )[:5]

        resultados = []
        for disc in qs:
            resultados.append({
                'tipo': 'disciplina',
                'id': disc.pk,
                'titulo': disc.nome,
                'subtitulo': f"{disc.codigo} — {disc.carga_horaria}h",
                'url': f'/academico/disciplina/{disc.slug}/',
                'slug': disc.slug,
                'icone': 'book',
                'badge': disc.departamento or 'Disciplina',
            })
        return resultados


class AgendaSalaAPIView(APIView):
    """
    Retorna agenda semanal de uma sala.
    GET /api/v1/busca/agenda-sala/<slug>/
    """
    permission_classes = [AllowAny]

    def get(self, request, slug):
        from apps.estrutura.models import Sala
        from apps.reservas.models import Reserva
        from datetime import date, timedelta

        try:
            sala = Sala.objects.get(slug=slug, ativo=True)
        except Sala.DoesNotExist:
            return Response({'erro': 'Sala não encontrada'}, status=404)

        hoje = date.today()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        fim_semana = inicio_semana + timedelta(days=6)

        reservas = Reserva.objects.filter(
            sala=sala,
            data_inicio__range=[inicio_semana, fim_semana],
            status=Reserva.Status.APROVADA
        ).select_related(
            'solicitante', 'turma__disciplina', 'turma__professor__usuario'
        ).order_by('data_inicio', 'hora_inicio')

        agenda = []
        for r in reservas:
            agenda.append({
                'id': r.pk,
                'data': r.data_inicio.strftime('%Y-%m-%d'),
                'data_br': r.data_inicio.strftime('%d/%m'),
                'dia_semana': r.data_inicio.strftime('%A'),
                'hora_inicio': r.hora_inicio.strftime('%H:%M'),
                'hora_fim': r.hora_fim.strftime('%H:%M'),
                'disciplina': str(r.turma.disciplina) if r.turma else r.motivo,
                'professor': str(r.turma.professor) if r.turma and r.turma.professor else str(r.solicitante),
                'turma': str(r.turma) if r.turma else '',
            })

        return Response({
            'sala': {
                'id': sala.pk,
                'nome': sala.nome,
                'codigo': sala.codigo,
                'tipo': sala.get_tipo_display(),
                'capacidade': sala.capacidade,
                'predio': sala.andar.predio.nome,
                'andar': str(sala.andar),
            },
            'semana': {
                'inicio': inicio_semana.strftime('%d/%m/%Y'),
                'fim': fim_semana.strftime('%d/%m/%Y'),
            },
            'agenda': agenda,
            'total_reservas': len(agenda),
        })


class AgendaProfessorAPIView(APIView):
    """Retorna agenda semanal de um professor."""
    permission_classes = [AllowAny]

    def get(self, request, slug):
        from apps.academico.models import Professor
        from apps.reservas.models import Reserva
        from datetime import date, timedelta

        try:
            prof = Professor.objects.get(slug=slug, ativo=True)
        except Professor.DoesNotExist:
            return Response({'erro': 'Professor não encontrado'}, status=404)

        hoje = date.today()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        fim_semana = inicio_semana + timedelta(days=6)

        reservas = Reserva.objects.filter(
            turma__professor=prof,
            data_inicio__range=[inicio_semana, fim_semana],
            status=Reserva.Status.APROVADA
        ).select_related('sala__andar__predio', 'turma__disciplina').order_by('data_inicio', 'hora_inicio')

        agenda = []
        for r in reservas:
            agenda.append({
                'data': r.data_inicio.strftime('%Y-%m-%d'),
                'data_br': r.data_inicio.strftime('%d/%m'),
                'hora_inicio': r.hora_inicio.strftime('%H:%M'),
                'hora_fim': r.hora_fim.strftime('%H:%M'),
                'disciplina': str(r.turma.disciplina) if r.turma else r.motivo,
                'sala': r.sala.nome,
                'sala_codigo': r.sala.codigo,
                'predio': r.sala.andar.predio.nome,
            })

        return Response({
            'professor': {
                'nome': prof.usuario.nome_completo,
                'siape': prof.siape,
                'area': prof.area_atuacao,
                'titulacao': prof.get_titulacao_display(),
            },
            'semana': {
                'inicio': inicio_semana.strftime('%d/%m/%Y'),
                'fim': fim_semana.strftime('%d/%m/%Y'),
            },
            'agenda': agenda,
        })


class HealthCheckAPIView(APIView):
    """Health check do sistema."""
    permission_classes = [AllowAny]

    def get(self, request):
        from django.db import connection
        try:
            connection.ensure_connection()
            db_ok = True
        except Exception:
            db_ok = False

        return Response({
            'status': 'ok' if db_ok else 'degraded',
            'database': 'ok' if db_ok else 'error',
            'version': '1.0.0',
        })
