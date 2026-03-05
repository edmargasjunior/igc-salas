"""
App: notificacoes
Sistema de notificações internas e e-mail.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Notificacao(models.Model):
    """Notificação interna no sistema."""

    class Tipo(models.TextChoices):
        RESERVA_APROVADA = 'reserva_aprovada', _('Reserva Aprovada')
        RESERVA_REJEITADA = 'reserva_rejeitada', _('Reserva Rejeitada')
        RESERVA_CANCELADA = 'reserva_cancelada', _('Reserva Cancelada')
        RESERVA_OVERRIDE = 'reserva_override', _('Reserva Substituída por Override')
        LEMBRETE = 'lembrete', _('Lembrete')
        SISTEMA = 'sistema', _('Mensagem do Sistema')

    destinatario = models.ForeignKey(
        'accounts.Usuario',
        on_delete=models.CASCADE,
        related_name='notificacoes',
        verbose_name=_('Destinatário')
    )
    tipo = models.CharField(max_length=25, choices=Tipo.choices, verbose_name=_('Tipo'))
    titulo = models.CharField(max_length=200, verbose_name=_('Título'))
    mensagem = models.TextField(verbose_name=_('Mensagem'))
    reserva = models.ForeignKey(
        'reservas.Reserva',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='notificacoes',
        verbose_name=_('Reserva Relacionada')
    )
    lida = models.BooleanField(default=False, verbose_name=_('Lida'))
    lida_em = models.DateTimeField(null=True, blank=True, verbose_name=_('Lida em'))
    email_enviado = models.BooleanField(default=False, verbose_name=_('E-mail Enviado'))
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Notificação')
        verbose_name_plural = _('Notificações')
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['destinatario', 'lida']),
        ]

    def __str__(self):
        return f"{self.titulo} → {self.destinatario}"

    def marcar_lida(self):
        from django.utils import timezone
        self.lida = True
        self.lida_em = timezone.now()
        self.save(update_fields=['lida', 'lida_em'])
