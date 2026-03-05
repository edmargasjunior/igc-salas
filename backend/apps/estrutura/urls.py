"""URLs públicas de estrutura: /salas/"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.SalaListaPublicaView.as_view(), name='salas_lista'),
    path('<slug:slug>/', views.SalaDetalhePublicaView.as_view(), name='sala_detalhe'),
]
