"""URLs da API de notificações."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.reservas.api_stats import NotificacoesRecentesAPIView

urlpatterns = [
    path('recentes/', NotificacoesRecentesAPIView.as_view(), name='api_notificacoes_recentes'),
]
