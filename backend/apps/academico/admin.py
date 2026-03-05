"""Admin para módulo acadêmico."""
from django.contrib import admin
from .models import Professor, Disciplina, Turma


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'siape', 'titulacao', 'area_atuacao', 'ativo']
    list_filter = ['titulacao', 'ativo']
    search_fields = ['usuario__first_name', 'usuario__last_name', 'siape']


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'carga_horaria', 'creditos', 'departamento', 'ativo']
    list_filter = ['modalidade', 'ativo', 'departamento']
    search_fields = ['codigo', 'nome']


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'disciplina', 'professor', 'ano', 'semestre', 'vagas', 'ativo']
    list_filter = ['ano', 'semestre', 'ativo']
    search_fields = ['codigo', 'disciplina__nome', 'professor__usuario__first_name']
