"""URLs de autenticação."""
from django.urls import path
from . import views

urlpatterns = [
    path('entrar/', views.LoginView.as_view(), name='login'),
    path('sair/', views.LogoutView.as_view(), name='logout'),
    path('perfil/', views.PerfilView.as_view(), name='perfil'),
]
