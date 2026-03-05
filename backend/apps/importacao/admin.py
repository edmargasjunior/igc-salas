"""Admin de importações CSV."""
from django.contrib import admin
from .models import ImportacaoCSV


@admin.register(ImportacaoCSV)
class ImportacaoCSVAdmin(admin.ModelAdmin):
    list_display = ['nome_arquivo', 'importado_por', 'status', 'total_linhas',
                    'linhas_sucesso', 'linhas_erro', 'linhas_conflito', 'criado_em']
    list_filter = ['status', 'criado_em']
    search_fields = ['nome_arquivo', 'importado_por__first_name']
    readonly_fields = ['importado_por', 'nome_arquivo', 'arquivo', 'status',
                       'total_linhas', 'linhas_sucesso', 'linhas_erro',
                       'linhas_conflito', 'relatorio', 'criado_em', 'concluido_em']
    date_hierarchy = 'criado_em'

    def has_add_permission(self, request):
        return False
