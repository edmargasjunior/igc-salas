"""URLs da API de reservas incluindo stats."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ReservaViewSet
from .api_stats import (
    ReservasStatsOcupacaoAPIView,
    ReservasStatsStatusAPIView,
    ReservasStatsTendenciaAPIView,
)

router = DefaultRouter()
router.register('', ReservaViewSet, basename='api-reserva')

urlpatterns = [
    path('stats/ocupacao/', ReservasStatsOcupacaoAPIView.as_view(), name='api_stats_ocupacao'),
    path('stats/status/', ReservasStatsStatusAPIView.as_view(), name='api_stats_status'),
    path('stats/tendencia/', ReservasStatsTendenciaAPIView.as_view(), name='api_stats_tendencia'),
    path('', include(router.urls)),
]
