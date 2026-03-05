"""URLs públicas: /professor/<slug>/"""
from django.urls import path
from . import views

urlpatterns = [
    path('<slug:slug>/', views.ProfessorDetalheView.as_view(), name='professor_detalhe'),
]
