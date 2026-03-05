"""
App: importacao
Importação de planejamento semestral via CSV.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class ImportacaoCSV(models.Model):
    """Registro de cada importação de CSV realizada."""

    class Status(models.TextChoices):
        PROCESSANDO = 'processando', _('Processando')
        CONCLUIDO = 'concluido', _('Concluído')
        ERRO = 'erro', _('Erro')
        CANCELADO = 'cancelado', _('Cancelado')

    importado_por = models.ForeignKey(
        'accounts.Usuario',
        on_delete=models.SET_NULL, null=True,
        verbose_name=_('Importado por')
    )
    arquivo = models.FileField(
        upload_to='importacoes/csv/',
        verbose_name=_('Arquivo CSV')
    )
    nome_arquivo = models.CharField(max_length=200, verbose_name=_('Nome do Arquivo'))
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PROCESSANDO
    )
    total_linhas = models.IntegerField(default=0, verbose_name=_('Total de Linhas'))
    linhas_sucesso = models.IntegerField(default=0, verbose_name=_('Linhas com Sucesso'))
    linhas_erro = models.IntegerField(default=0, verbose_name=_('Linhas com Erro'))
    linhas_conflito = models.IntegerField(default=0, verbose_name=_('Linhas com Conflito'))
    relatorio = models.JSONField(default=list, verbose_name=_('Relatório Detalhado'))
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    concluido_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Importação CSV')
        verbose_name_plural = _('Importações CSV')
        ordering = ['-criado_em']

    def __str__(self):
        return f"Importação {self.nome_arquivo} ({self.criado_em.strftime('%d/%m/%Y')})"
