from django.urls import path
from django.views.generic import TemplateView

# URL pública: /salas/<slug>/
urlpatterns = [
    path('<slug:slug>/', TemplateView.as_view(template_name='estrutura/detalhe.html'), name='sala_detalhe'),
]
