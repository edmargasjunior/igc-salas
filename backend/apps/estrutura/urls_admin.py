"""URLs administrativas de estrutura (autenticadas)."""
from django.urls import path
from . import views

urlpatterns = [
    path('salas/', views.SalaListaAdminView.as_view(), name='salas_admin'),
    path('predios/', views.PredioListaAdminView.as_view(), name='predios_admin'),
    path('equipamentos/', views.EquipamentoListaView.as_view(), name='equipamentos_lista'),
]
