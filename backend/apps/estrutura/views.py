"""Views do módulo estrutura: Salas, Laboratórios, Prédios, Equipamentos."""
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages

from .models import Sala, Predio, Andar, Equipamento


# ──────────────────────────── VIEWS PÚBLICAS ────────────────────────────

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


# ──────────────────────────── VIEWS ADMIN SALAS ────────────────────────────

class SalaListaAdminView(View):
    """Lista de salas para gestão administrativa."""
    template_name = 'estrutura/salas_admin.html'

    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_responsavel:
            messages.error(request, 'Acesso restrito a responsáveis e administradores.')
            return redirect('dashboard')
        q = request.GET.get('q', '')
        predio_id = request.GET.get('predio', '')
        salas = Sala.objects.filter(ativo=True).select_related('andar__predio').annotate(
            total_equipamentos=Count('equipamentos', filter=Q(equipamentos__ativo=True))
        )
        if q:
            salas = salas.filter(Q(nome__icontains=q) | Q(codigo__icontains=q))
        if predio_id:
            salas = salas.filter(andar__predio_id=predio_id)
        salas = salas.order_by('andar__predio__codigo', 'andar__numero', 'codigo')
        predios = Predio.objects.filter(ativo=True)
        return render(request, self.template_name, {
            'salas': salas, 'predios': predios
        })


class SalaCriarView(View):
    """Criar nova sala."""
    template_name = 'estrutura/sala_form.html'

    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_responsavel:
            return redirect('dashboard')
        predios = Predio.objects.filter(ativo=True)
        andares = Andar.objects.filter(ativo=True).select_related('predio')
        return render(request, self.template_name, {
            'sala': None,
            'predios': predios,
            'andares': andares,
            'tipo_choices': Sala.Tipo.choices,
            'status_choices': Sala.Status.choices,
        })

    @method_decorator(login_required)
    def post(self, request):
        if not request.user.is_responsavel:
            return redirect('dashboard')
        try:
            andar_id = request.POST.get('andar_id')
            andar = get_object_or_404(Andar, pk=andar_id)
            sala = Sala(
                codigo=request.POST.get('codigo', '').strip(),
                nome=request.POST.get('nome', '').strip(),
                tipo=request.POST.get('tipo', Sala.Tipo.SALA_AULA),
                andar=andar,
                capacidade=int(request.POST.get('capacidade', 30)),
                area_m2=request.POST.get('area_m2') or None,
                status=request.POST.get('status', Sala.Status.DISPONIVEL),
                tem_projetor='tem_projetor' in request.POST,
                tem_ar_condicionado='tem_ar_condicionado' in request.POST,
                tem_lousa_digital='tem_lousa_digital' in request.POST,
                tem_videoconferencia='tem_videoconferencia' in request.POST,
                tem_acessibilidade='tem_acessibilidade' in request.POST,
                tem_computadores='tem_computadores' in request.POST,
                qtd_computadores=int(request.POST.get('qtd_computadores', 0)),
                observacoes=request.POST.get('observacoes', ''),
            )
            sala.full_clean()
            sala.save()
            messages.success(request, f'Sala {sala.codigo} criada com sucesso!')
            return redirect('salas_admin')
        except Exception as e:
            messages.error(request, f'Erro ao criar sala: {e}')
            return redirect('salas_admin')


class SalaEditarView(View):
    """Editar sala existente."""
    template_name = 'estrutura/sala_form.html'

    @method_decorator(login_required)
    def get(self, request, pk):
        if not request.user.is_responsavel:
            return redirect('dashboard')
        sala = get_object_or_404(Sala, pk=pk)
        predios = Predio.objects.filter(ativo=True)
        andares = Andar.objects.filter(predio=sala.andar.predio, ativo=True)
        return render(request, self.template_name, {
            'sala': sala,
            'predios': predios,
            'andares': andares,
            'tipo_choices': Sala.Tipo.choices,
            'status_choices': Sala.Status.choices,
        })

    @method_decorator(login_required)
    def post(self, request, pk):
        if not request.user.is_responsavel:
            return redirect('dashboard')
        sala = get_object_or_404(Sala, pk=pk)
        try:
            andar_id = request.POST.get('andar_id')
            sala.andar = get_object_or_404(Andar, pk=andar_id)
            sala.codigo = request.POST.get('codigo', sala.codigo).strip()
            sala.nome = request.POST.get('nome', sala.nome).strip()
            sala.tipo = request.POST.get('tipo', sala.tipo)
            sala.capacidade = int(request.POST.get('capacidade', sala.capacidade))
            sala.area_m2 = request.POST.get('area_m2') or sala.area_m2
            sala.status = request.POST.get('status', sala.status)
            sala.tem_projetor = 'tem_projetor' in request.POST
            sala.tem_ar_condicionado = 'tem_ar_condicionado' in request.POST
            sala.tem_lousa_digital = 'tem_lousa_digital' in request.POST
            sala.tem_videoconferencia = 'tem_videoconferencia' in request.POST
            sala.tem_acessibilidade = 'tem_acessibilidade' in request.POST
            sala.tem_computadores = 'tem_computadores' in request.POST
            sala.qtd_computadores = int(request.POST.get('qtd_computadores', 0))
            sala.observacoes = request.POST.get('observacoes', sala.observacoes)
            sala.save()
            messages.success(request, f'Sala {sala.codigo} atualizada com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar sala: {e}')
        return redirect('salas_admin')


class SalaExcluirView(View):
    """Excluir (desativar) sala."""
    @method_decorator(login_required)
    def post(self, request, pk):
        if not request.user.is_admin:
            messages.error(request, 'Apenas administradores podem excluir salas.')
            return redirect('salas_admin')
        sala = get_object_or_404(Sala, pk=pk)
        sala.ativo = False
        sala.save()
        messages.success(request, f'Sala {sala.codigo} removida.')
        return redirect('salas_admin')


# ──────────────────────────── VIEWS ADMIN PREDIOS ────────────────────────────

class PredioListaAdminView(View):
    """Lista de prédios para gestão administrativa."""
    template_name = 'estrutura/predios_admin.html'

    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_responsavel:
            return redirect('dashboard')
        predios = Predio.objects.filter(ativo=True).annotate(
            total_salas=Count('andares__salas', filter=Q(andares__salas__ativo=True))
        ).prefetch_related('andares').order_by('nome')
        return render(request, self.template_name, {'predios': predios})


# ──────────────────────────── VIEWS ADMIN EQUIPAMENTOS ────────────────────────────

class EquipamentoListaView(View):
    """Lista de equipamentos por sala."""
    template_name = 'estrutura/equipamentos.html'

    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_responsavel:
            return redirect('dashboard')
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


class EquipamentoCriarView(View):
    template_name = 'estrutura/equipamento_form.html'

    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_responsavel:
            return redirect('dashboard')
        salas = Sala.objects.filter(ativo=True).select_related('andar__predio')
        return render(request, self.template_name, {
            'equipamento': None,
            'salas': salas,
            'estado_choices': Equipamento.EstadoConservacao.choices,
        })

    @method_decorator(login_required)
    def post(self, request):
        if not request.user.is_responsavel:
            return redirect('dashboard')
        try:
            sala_id = request.POST.get('sala_id')
            sala = get_object_or_404(Sala, pk=sala_id)
            eq = Equipamento(
                nome=request.POST.get('nome', '').strip(),
                quantidade=int(request.POST.get('quantidade', 1)),
                patrimonio=request.POST.get('patrimonio', '').strip() or None,
                numero_serie=request.POST.get('numero_serie', '').strip(),
                modelo=request.POST.get('modelo', '').strip(),
                fabricante=request.POST.get('fabricante', '').strip(),
                sala=sala,
                estado_conservacao=request.POST.get('estado_conservacao', 'bom'),
                data_aquisicao=request.POST.get('data_aquisicao') or None,
                data_garantia=request.POST.get('data_garantia') or None,
                valor_aquisicao=request.POST.get('valor_aquisicao') or None,
                observacoes=request.POST.get('observacoes', ''),
            )
            eq.save()
            messages.success(request, f'Equipamento "{eq.nome}" cadastrado com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro: {e}')
        return redirect('equipamentos_lista')


class EquipamentoEditarView(View):
    template_name = 'estrutura/equipamento_form.html'

    @method_decorator(login_required)
    def get(self, request, pk):
        if not request.user.is_responsavel:
            return redirect('dashboard')
        eq = get_object_or_404(Equipamento, pk=pk)
        salas = Sala.objects.filter(ativo=True).select_related('andar__predio')
        return render(request, self.template_name, {
            'equipamento': eq,
            'salas': salas,
            'estado_choices': Equipamento.EstadoConservacao.choices,
        })

    @method_decorator(login_required)
    def post(self, request, pk):
        if not request.user.is_responsavel:
            return redirect('dashboard')
        eq = get_object_or_404(Equipamento, pk=pk)
        try:
            sala_id = request.POST.get('sala_id')
            eq.sala = get_object_or_404(Sala, pk=sala_id)
            eq.nome = request.POST.get('nome', eq.nome).strip()
            eq.quantidade = int(request.POST.get('quantidade', eq.quantidade))
            eq.patrimonio = request.POST.get('patrimonio', '').strip() or None
            eq.numero_serie = request.POST.get('numero_serie', eq.numero_serie)
            eq.modelo = request.POST.get('modelo', eq.modelo)
            eq.fabricante = request.POST.get('fabricante', eq.fabricante)
            eq.estado_conservacao = request.POST.get('estado_conservacao', eq.estado_conservacao)
            eq.data_aquisicao = request.POST.get('data_aquisicao') or eq.data_aquisicao
            eq.data_garantia = request.POST.get('data_garantia') or eq.data_garantia
            eq.valor_aquisicao = request.POST.get('valor_aquisicao') or eq.valor_aquisicao
            eq.observacoes = request.POST.get('observacoes', eq.observacoes)
            eq.save()
            messages.success(request, f'Equipamento "{eq.nome}" atualizado.')
        except Exception as e:
            messages.error(request, f'Erro: {e}')
        return redirect('equipamentos_lista')


class EquipamentoExcluirView(View):
    @method_decorator(login_required)
    def post(self, request, pk):
        if not request.user.is_responsavel:
            return redirect('dashboard')
        eq = get_object_or_404(Equipamento, pk=pk)
        eq.ativo = False
        eq.save()
        messages.success(request, f'Equipamento "{eq.nome}" removido.')
        return redirect('equipamentos_lista')


# ──────────────────────────── API: Andares por Prédio ────────────────────────────

class AndaresAPIView(View):
    """Retorna andares de um prédio via JSON (uso no formulário de salas)."""
    def get(self, request):
        predio_id = request.GET.get('predio')
        andares = Andar.objects.filter(predio_id=predio_id, ativo=True).order_by('numero')
        data = [{'id': a.pk, 'nome': a.nome_display, 'numero': a.numero} for a in andares]
        return JsonResponse(data, safe=False)
