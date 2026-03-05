"""Admin do módulo acadêmico."""
from django.contrib import admin
from .models import Professor, Disciplina, Turma


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'siape', 'titulacao', 'area_atuacao', 'ativo']
    list_filter = ['titulacao', 'ativo']
    search_fields = ['usuario__first_name', 'usuario__last_name', 'siape']
    raw_id_fields = ['usuario']
    prepopulated_fields = {'slug': []}
    list_per_page = 30


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'carga_horaria', 'creditos', 'modalidade', 'departamento', 'ativo']
    list_filter = ['modalidade', 'ativo', 'departamento']
    search_fields = ['nome', 'codigo']
    prepopulated_fields = {'slug': []}
    list_per_page = 30


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'disciplina', 'professor', 'ano', 'semestre', 'vagas', 'matriculados', 'ativo']
    list_filter = ['ano', 'semestre', 'ativo']
    search_fields = ['codigo', 'disciplina__nome', 'disciplina__codigo', 'professor__usuario__first_name']
    raw_id_fields = ['disciplina', 'professor']
    list_per_page = 30
