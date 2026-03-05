"""URLs de importação CSV."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ImportacaoIndexView.as_view(), name='importacao_index'),
]
