"""Admin para estrutura física."""
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


@admin.register(Predio)
class PredioAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'endereco', 'ativo']
    list_filter = ['ativo']
    search_fields = ['codigo', 'nome']
    prepopulated_fields = {'slug': ('nome',)}
    inlines = [AndarInline]


@admin.register(Andar)
class AndarAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'predio', 'numero', 'nome', 'ativo']
    list_filter = ['predio', 'ativo']


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'tipo', 'capacidade', 'status', 'predio_display', 'ativo']
    list_filter = ['tipo', 'status', 'ativo', 'andar__predio']
    search_fields = ['codigo', 'nome']
    prepopulated_fields = {'slug': ('nome',)}
    list_editable = ['status', 'ativo']
    inlines = [EquipamentoInline]

    def predio_display(self, obj):
        return obj.andar.predio.codigo
    predio_display.short_description = 'Prédio'


@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ['patrimonio', 'nome', 'sala', 'fabricante', 'estado_conservacao', 'garantia_vigente']
    list_filter = ['estado_conservacao', 'sala__andar__predio']
    search_fields = ['nome', 'patrimonio', 'modelo', 'fabricante']
