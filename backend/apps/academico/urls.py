"""URLs acadêmicas para gestão (autenticadas)."""
from django.urls import path
from . import views

urlpatterns = [
    path('professores/', views.ProfessorListaView.as_view(), name='professores_lista'),
    path('turmas/', views.TurmaListaView.as_view(), name='turmas_lista'),
]
