"""URLs da API de estrutura física."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import PredioViewSet, SalaViewSet, EquipamentoViewSet

router = DefaultRouter()
router.register('predios', PredioViewSet, basename='api-predio')
router.register('salas', SalaViewSet, basename='api-sala')
router.register('equipamentos', EquipamentoViewSet, basename='api-equipamento')

urlpatterns = [
    path('', include(router.urls)),
]
