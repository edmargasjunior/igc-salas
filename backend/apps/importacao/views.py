"""Views de importação CSV."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from django.utils import timezone

from .models import ImportacaoCSV
from .processador import ProcessadorCSV


class ImportacaoIndexView(View):
    template_name = 'importacao/index.html'

    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_responsavel:
            messages.error(request, 'Acesso restrito.')
            return redirect('dashboard')
        historico = ImportacaoCSV.objects.filter(
            importado_por=request.user
        ).order_by('-criado_em')[:10]
        return render(request, self.template_name, {'historico': historico})

    @method_decorator(login_required)
    def post(self, request):
        if not request.user.is_responsavel:
            messages.error(request, 'Acesso restrito.')
            return redirect('dashboard')

        arquivo = request.FILES.get('arquivo_csv')
        if not arquivo:
            messages.error(request, 'Selecione um arquivo CSV.')
            return redirect('importacao_index')

        if not arquivo.name.endswith('.csv'):
            messages.error(request, 'O arquivo deve ter extensão .csv')
            return redirect('importacao_index')

        conteudo = arquivo.read()
        processador = ProcessadorCSV(request.user)
        acao = request.POST.get('acao', 'validar')

        # Registrar importação
        importacao = ImportacaoCSV.objects.create(
            importado_por=request.user,
            arquivo=arquivo,
            nome_arquivo=arquivo.name,
            status=ImportacaoCSV.Status.PROCESSANDO,
        )

        if acao == 'validar':
            relatorio = processador.processar(conteudo)
            importacao.total_linhas = relatorio['total_linhas']
            importacao.linhas_sucesso = relatorio['validas']
            importacao.linhas_erro = relatorio['erros']
            importacao.linhas_conflito = relatorio['conflitos']
            importacao.relatorio = relatorio
            importacao.status = ImportacaoCSV.Status.CONCLUIDO
            importacao.concluido_em = timezone.now()
            importacao.save()
            return render(request, self.template_name, {
                'relatorio': relatorio,
                'importacao': importacao,
                'conteudo_b64': conteudo.decode('utf-8-sig', errors='replace'),
                'nome_arquivo': arquivo.name,
                'historico': ImportacaoCSV.objects.filter(importado_por=request.user).order_by('-criado_em')[:10],
            })

        elif acao == 'confirmar':
            resultado = processador.importar(conteudo)
            importacao.linhas_sucesso = resultado['importadas']
            importacao.linhas_erro = len(resultado['erros_importacao'])
            importacao.status = ImportacaoCSV.Status.CONCLUIDO
            importacao.concluido_em = timezone.now()
            importacao.save()
            messages.success(
                request,
                f"✅ Importação concluída: {resultado['importadas']} reservas criadas, "
                f"{resultado['conflitos_ignorados']} conflitos ignorados."
            )
            return redirect('importacao_index')

        return redirect('importacao_index')
