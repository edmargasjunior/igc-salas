"""URLs de autenticação completas."""
from django.urls import path
from . import views

urlpatterns = [
    path('entrar/', views.LoginView.as_view(), name='login'),
    path('sair/', views.LogoutView.as_view(), name='logout'),
    path('recuperar-senha/', views.RecuperarSenhaView.as_view(), name='recuperar_senha'),
    path('perfil/', views.PerfilView.as_view(), name='perfil'),
]
