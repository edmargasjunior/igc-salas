"""URLs do dashboard."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('ocupacao/', views.DashboardOcupacaoView.as_view(), name='dashboard_ocupacao'),
]
