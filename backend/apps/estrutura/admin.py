"""Admin da estrutura física."""
from django.contrib import admin
from .models import Predio, Andar, Sala, Equipamento


class AndarInline(admin.TabularInline):
    model = Andar
    extra = 1
    fields = ['numero', 'nome', 'ativo']


class EquipamentoInline(admin.TabularInline):
    model = Equipamento
    extra = 0
    fields = ['nome', 'patrimonio', 'modelo', 'quantidade', 'estado_conservacao', 'ativo']
    show_change_link = True


@admin.register(Predio)
class PredioAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'endereco', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'codigo']
    prepopulated_fields = {'slug': ['nome']}
    inlines = [AndarInline]


@admin.register(Andar)
class AndarAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'predio', 'numero', 'nome', 'ativo']
    list_filter = ['predio', 'ativo']
    search_fields = ['predio__nome', 'nome']


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'tipo', 'capacidade', 'status',
                    'tem_projetor', 'tem_ar_condicionado', 'ativo']
    list_filter = ['tipo', 'status', 'ativo', 'andar__predio',
                   'tem_projetor', 'tem_ar_condicionado', 'tem_videoconferencia']
    search_fields = ['nome', 'codigo', 'andar__predio__nome']
    list_editable = ['status', 'ativo']
    prepopulated_fields = {'slug': []}
    inlines = [EquipamentoInline]
    fieldsets = (
        ('Identificação', {
            'fields': ('andar', 'codigo', 'nome', 'slug', 'tipo', 'status')
        }),
        ('Capacidade e Área', {
            'fields': ('capacidade', 'area_m2')
        }),
        ('Recursos Disponíveis', {
            'fields': ('tem_projetor', 'tem_ar_condicionado', 'tem_lousa_digital',
                       'tem_videoconferencia', 'tem_acessibilidade',
                       'tem_computadores', 'qtd_computadores', 'observacoes_recursos')
        }),
        ('Outros', {
            'fields': ('descricao', 'foto', 'ativo')
        }),
    )


@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ['patrimonio', 'nome', 'modelo', 'fabricante',
                    'sala', 'quantidade', 'estado_conservacao', 'garantia_vigente', 'ativo']
    list_filter = ['estado_conservacao', 'ativo', 'sala__andar__predio']
    search_fields = ['nome', 'patrimonio', 'modelo', 'fabricante', 'numero_serie']
    raw_id_fields = ['sala']
    date_hierarchy = 'data_aquisicao'
