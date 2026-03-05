"""URLs da API core."""
from django.urls import path
from .api_busca import HealthCheckAPIView

urlpatterns = [
    path('health/', HealthCheckAPIView.as_view(), name='api_health'),
]
