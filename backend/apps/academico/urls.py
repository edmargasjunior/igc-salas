"""URLs acadêmicas para gestão (autenticadas)."""
from django.urls import path
from . import views

urlpatterns = [
    # Professores
    path('professores/', views.ProfessorListaView.as_view(), name='professores_lista'),
    path('professores/novo/', views.ProfessorCriarView.as_view(), name='professor_criar'),
    path('professores/<int:pk>/editar/', views.ProfessorEditarView.as_view(), name='professor_editar'),

    # Turmas
    path('turmas/', views.TurmaListaView.as_view(), name='turmas_lista'),
    path('turmas/nova/', views.TurmaCriarView.as_view(), name='turma_criar'),
    path('turmas/<int:pk>/editar/', views.TurmaEditarView.as_view(), name='turma_editar'),

    # Disciplinas
    path('disciplinas/<slug:slug>/', views.DisciplinaDetalheView.as_view(), name='disciplina_detalhe'),
]
