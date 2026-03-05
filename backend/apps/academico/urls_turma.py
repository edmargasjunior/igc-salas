"""URLs públicas: /turma/<slug>/"""
from django.urls import path
from . import views

urlpatterns = [
    path('<slug:slug>/', views.TurmaDetalheView.as_view(), name='turma_detalhe'),
]
