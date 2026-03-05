"""Views do sistema de reservas."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.http import JsonResponse

from .models import Reserva, LogReserva
from .services import ReservaService


class ReservaListView(View):
    template_name = 'reservas/lista.html'

    @method_decorator(login_required)
    def get(self, request):
        qs = Reserva.objects.filter(
            solicitante=request.user
        ).select_related('sala__andar__predio', 'turma__disciplina').order_by('-criado_em')

        status_filtro = request.GET.get('status', '')
        if status_filtro:
            qs = qs.filter(status=status_filtro)

        return render(request, self.template_name, {
            'reservas': qs[:50],
            'status_choices': Reserva.Status.choices,
            'status_filtro': status_filtro,
        })


class ReservaDetalheView(View):
    template_name = 'reservas/detalhe.html'

    @method_decorator(login_required)
    def get(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)

        # Verificar permissão
        if not (request.user == reserva.solicitante or request.user.is_responsavel):
            messages.error(request, 'Sem permissão para ver esta reserva.')
            return redirect('reservas_lista')

        logs = LogReserva.objects.filter(reserva=reserva).order_by('-criado_em')
        return render(request, self.template_name, {'reserva': reserva, 'logs': logs})


class ReservaNova(View):
    template_name = 'reservas/form.html'

    @method_decorator(login_required)
    def get(self, request):
        from apps.estrutura.models import Sala
        from apps.academico.models import Turma

        salas = Sala.objects.filter(ativo=True, status='disponivel').select_related('andar__predio')
        turmas = []
        if request.user.is_professor:
            try:
                turmas = Turma.objects.filter(
                    professor__usuario=request.user,
                    ativo=True
                ).select_related('disciplina')
            except Exception:
                pass

        return render(request, self.template_name, {
            'salas': salas,
            'turmas': turmas,
            'tipo_choices': Reserva.Tipo.choices,
        })

    @method_decorator(login_required)
    def post(self, request):
        from apps.estrutura.models import Sala
        from apps.academico.models import Turma
        from datetime import date, time

        service = ReservaService()
        try:
            sala_id = request.POST.get('sala')
            sala = get_object_or_404(Sala, pk=sala_id)

            turma_id = request.POST.get('turma')
            turma = Turma.objects.get(pk=turma_id) if turma_id else None

            dados = {
                'sala': sala,
                'turma': turma,
                'tipo': request.POST.get('tipo', Reserva.Tipo.PONTUAL),
                'data_inicio': request.POST.get('data_inicio'),
                'data_fim': request.POST.get('data_fim') or None,
                'hora_inicio': request.POST.get('hora_inicio'),
                'hora_fim': request.POST.get('hora_fim'),
                'motivo': request.POST.get('motivo', ''),
                'observacoes': request.POST.get('observacoes', ''),
            }

            reserva = service.criar_reserva(dados, request.user, request)
            messages.success(request, f'Reserva #{reserva.pk} criada com sucesso! Status: {reserva.get_status_display()}')
            return redirect('reserva_detalhe', pk=reserva.pk)

        except ValidationError as e:
            messages.error(request, str(e.message if hasattr(e, 'message') else e))
        except Exception as e:
            messages.error(request, f'Erro ao criar reserva: {str(e)}')

        return redirect('reserva_nova')


class ReservaAprovarView(View):
    @method_decorator(login_required)
    def get(self, request, pk):
        if not request.user.pode_aprovar_reservas():
            messages.error(request, 'Sem permissão.')
            return redirect('dashboard')

        reserva = get_object_or_404(Reserva, pk=pk)
        service = ReservaService()
        try:
            service.aprovar_reserva(reserva, request.user, request)
            messages.success(request, f'Reserva #{pk} aprovada com sucesso!')
        except ValidationError as e:
            messages.error(request, str(e))

        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


class ReservaRejeitarView(View):
    template_name = 'reservas/rejeitar.html'

    @method_decorator(login_required)
    def get(self, request, pk):
        if not request.user.pode_aprovar_reservas():
            messages.error(request, 'Sem permissão.')
            return redirect('dashboard')
        reserva = get_object_or_404(Reserva, pk=pk)
        return render(request, self.template_name, {'reserva': reserva})

    @method_decorator(login_required)
    def post(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)
        motivo = request.POST.get('motivo', '').strip()
        if not motivo:
            messages.error(request, 'Informe o motivo da rejeição.')
            return render(request, self.template_name, {'reserva': reserva})

        service = ReservaService()
        try:
            service.rejeitar_reserva(reserva, request.user, motivo, request)
            messages.success(request, f'Reserva #{pk} rejeitada.')
        except ValidationError as e:
            messages.error(request, str(e))

        return redirect('dashboard')


class ReservasPendentesView(View):
    template_name = 'reservas/pendentes.html'

    @method_decorator(login_required)
    def get(self, request):
        if not request.user.pode_aprovar_reservas():
            messages.error(request, 'Sem permissão.')
            return redirect('dashboard')

        pendentes = Reserva.objects.filter(
            status=Reserva.Status.PENDENTE
        ).select_related(
            'sala__andar__predio', 'solicitante', 'turma__disciplina', 'turma__professor__usuario'
        ).order_by('data_inicio', 'hora_inicio')

        return render(request, self.template_name, {'pendentes': pendentes})


class ReservaOverrideView(View):
    template_name = 'reservas/override.html'

    @method_decorator(login_required)
    def get(self, request, pk):
        if not request.user.pode_fazer_override():
            messages.error(request, 'Apenas administradores podem realizar override.')
            return redirect('dashboard')
        reserva = get_object_or_404(Reserva, pk=pk)
        return render(request, self.template_name, {'reserva': reserva})

    @method_decorator(login_required)
    def post(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)
        motivo = request.POST.get('motivo', '').strip()

        nova_dados = {
            'sala': reserva.sala,
            'data_inicio': request.POST.get('data_inicio') or str(reserva.data_inicio),
            'hora_inicio': request.POST.get('hora_inicio') or str(reserva.hora_inicio),
            'hora_fim': request.POST.get('hora_fim') or str(reserva.hora_fim),
            'motivo': request.POST.get('motivo_nova', ''),
        }

        service = ReservaService()
        try:
            nova = service.override_reserva(reserva, nova_dados, request.user, motivo, request)
            messages.success(request, f'Override realizado. Nova reserva #{nova.pk} criada.')
        except ValidationError as e:
            messages.error(request, str(e))

        return redirect('dashboard')
