from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('<slug:slug>/', TemplateView.as_view(template_name='academico/professor.html'), name='professor_detalhe'),
]
