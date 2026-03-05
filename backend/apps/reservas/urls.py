"""URLs das reservas."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ReservaListView.as_view(), name='reservas_lista'),
    path('nova/', views.ReservaNova.as_view(), name='reserva_nova'),
    path('pendentes/', views.ReservasPendentesView.as_view(), name='reservas_pendentes'),
    path('<int:pk>/', views.ReservaDetalheView.as_view(), name='reserva_detalhe'),
    path('<int:pk>/aprovar/', views.ReservaAprovarView.as_view(), name='reserva_aprovar'),
    path('<int:pk>/rejeitar/', views.ReservaRejeitarView.as_view(), name='reserva_rejeitar'),
    path('<int:pk>/override/', views.ReservaOverrideView.as_view(), name='reserva_override'),
]
