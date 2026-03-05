"""URLs da API de Reservas."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ReservaViewSet

router = DefaultRouter()
router.register('', ReservaViewSet, basename='reserva')

urlpatterns = [path('', include(router.urls))]
