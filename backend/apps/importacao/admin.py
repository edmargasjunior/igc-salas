from django.contrib import admin
from .models import ImportacaoCSV

@admin.register(ImportacaoCSV)
class ImportacaoCSVAdmin(admin.ModelAdmin):
    list_display = ['nome_arquivo', 'importado_por', 'status', 'total_linhas', 'linhas_sucesso', 'linhas_erro', 'criado_em']
    list_filter = ['status']
    readonly_fields = ['relatorio', 'criado_em', 'concluido_em']
