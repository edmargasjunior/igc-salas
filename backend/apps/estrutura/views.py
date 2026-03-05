"""Views do módulo estrutura: Salas, Laboratórios, Prédios, Equipamentos."""
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone

from .models import Sala, Predio, Andar, Equipamento


class SalaDetalhePublicaView(View):
    """Página pública de detalhe de sala com agenda semanal. URL: /salas/<slug>/"""
    template_name = 'estrutura/detalhe.html'

    def get(self, request, slug):
        sala = get_object_or_404(Sala, slug=slug, ativo=True)
        hoje = timezone.now().date()
        from datetime import timedelta
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        fim_semana = inicio_semana + timedelta(days=6)

        from apps.reservas.models import Reserva
        reservas_semana = Reserva.objects.filter(
            sala=sala,
            data_inicio__range=[inicio_semana, fim_semana],
            status=Reserva.Status.APROVADA
        ).select_related(
            'solicitante', 'turma__disciplina', 'turma__professor__usuario'
        ).order_by('data_inicio', 'hora_inicio')

        equipamentos = Equipamento.objects.filter(sala=sala, ativo=True).order_by('nome')

        # Organizar agenda por dia da semana
        dias = {}
        for i in range(6):
            dia = inicio_semana + timedelta(days=i)
            dias[dia] = []
        for r in reservas_semana:
            if r.data_inicio in dias:
                dias[r.data_inicio].append(r)

        return render(request, self.template_name, {
            'sala': sala,
            'equipamentos': equipamentos,
            'dias_agenda': dias,
            'semana_inicio': inicio_semana,
            'semana_fim': fim_semana,
            'hoje': hoje,
        })


class SalaListaPublicaView(View):
    """Lista pública de todas as salas e laboratórios. URL: /salas/"""
    template_name = 'estrutura/lista.html'

    def get(self, request):
        tipo = request.GET.get('tipo', '')
        predio_id = request.GET.get('predio', '')
        q = request.GET.get('q', '')

        salas = Sala.objects.filter(ativo=True).select_related('andar__predio').order_by(
            'andar__predio__codigo', 'andar__numero', 'codigo'
        )
        if tipo:
            salas = salas.filter(tipo=tipo)
        if predio_id:
            salas = salas.filter(andar__predio_id=predio_id)
        if q:
            salas = salas.filter(Q(nome__icontains=q) | Q(codigo__icontains=q))

        predios = Predio.objects.filter(ativo=True).order_by('nome')
        tipos = Sala.Tipo.choices

        return render(request, self.template_name, {
            'salas': salas,
            'predios': predios,
            'tipos': tipos,
            'tipo_sel': tipo,
            'predio_sel': predio_id,
            'q': q,
        })


class SalaListaAdminView(View):
    """Lista de salas para gestão administrativa."""
    template_name = 'estrutura/salas_admin.html'

    @method_decorator(login_required)
    def get(self, request):
        salas = Sala.objects.filter(ativo=True).select_related('andar__predio').annotate(
            total_equipamentos=Count('equipamentos', filter=Q(equipamentos__ativo=True))
        ).order_by('andar__predio__codigo', 'andar__numero', 'codigo')
        predios = Predio.objects.filter(ativo=True)
        return render(request, self.template_name, {
            'salas': salas, 'predios': predios
        })


class PredioListaAdminView(View):
    """Lista de prédios para gestão administrativa."""
    template_name = 'estrutura/predios_admin.html'

    @method_decorator(login_required)
    def get(self, request):
        predios = Predio.objects.filter(ativo=True).annotate(
            total_salas=Count('andares__salas', filter=Q(andares__salas__ativo=True))
        ).order_by('nome')
        return render(request, self.template_name, {'predios': predios})


class EquipamentoListaView(View):
    """Lista de equipamentos por sala."""
    template_name = 'estrutura/equipamentos.html'

    @method_decorator(login_required)
    def get(self, request):
        q = request.GET.get('q', '')
        sala_id = request.GET.get('sala', '')
        equips = Equipamento.objects.filter(ativo=True).select_related('sala__andar__predio')
        if q:
            equips = equips.filter(
                Q(nome__icontains=q) | Q(patrimonio__icontains=q) | Q(modelo__icontains=q)
            )
        if sala_id:
            equips = equips.filter(sala_id=sala_id)
        equips = equips.order_by('sala__andar__predio__codigo', 'sala__codigo', 'nome')
        salas = Sala.objects.filter(ativo=True).select_related('andar__predio')
        return render(request, self.template_name, {
            'equipamentos': equips, 'salas': salas, 'q': q
        })
