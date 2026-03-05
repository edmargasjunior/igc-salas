"""URLs da API de busca."""
from django.urls import path
from .api_busca import BuscaGlobalAPIView, AgendaSalaAPIView, AgendaProfessorAPIView, HealthCheckAPIView

urlpatterns = [
    path('', BuscaGlobalAPIView.as_view(), name='api_busca'),
    path('agenda-sala/<slug:slug>/', AgendaSalaAPIView.as_view(), name='api_agenda_sala'),
    path('agenda-professor/<slug:slug>/', AgendaProfessorAPIView.as_view(), name='api_agenda_professor'),
]
