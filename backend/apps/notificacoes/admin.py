from django.contrib import admin
from .models import Notificacao

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'destinatario', 'tipo', 'lida', 'criado_em']
    list_filter = ['tipo', 'lida', 'email_enviado']
