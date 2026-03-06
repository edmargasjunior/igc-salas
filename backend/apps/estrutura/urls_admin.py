"""URLs administrativas de estrutura (autenticadas)."""
from django.urls import path
from . import views

urlpatterns = [
    # Salas
    path('salas/', views.SalaListaAdminView.as_view(), name='salas_admin'),
    path('salas/nova/', views.SalaCriarView.as_view(), name='sala_criar'),
    path('salas/<int:pk>/editar/', views.SalaEditarView.as_view(), name='sala_editar'),
    path('salas/<int:pk>/excluir/', views.SalaExcluirView.as_view(), name='sala_excluir'),

    # Prédios
    path('predios/', views.PredioListaAdminView.as_view(), name='predios_admin'),

    # Equipamentos
    path('equipamentos/', views.EquipamentoListaView.as_view(), name='equipamentos_lista'),
    path('equipamentos/novo/', views.EquipamentoCriarView.as_view(), name='equipamento_criar'),
    path('equipamentos/<int:pk>/editar/', views.EquipamentoEditarView.as_view(), name='equipamento_editar'),
    path('equipamentos/<int:pk>/excluir/', views.EquipamentoExcluirView.as_view(), name='equipamento_excluir'),

    # API interna
    path('api/andares/', views.AndaresAPIView.as_view(), name='api_andares'),
]
