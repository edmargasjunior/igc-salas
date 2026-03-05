"""Serviço de notificações - e-mail e internas."""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import logging

from .models import Notificacao

logger = logging.getLogger('apps.notificacoes')


class NotificacaoService:

    def notificar_aprovacao(self, reserva):
        msg = (f"Sua reserva para {reserva.sala.nome} em "
               f"{reserva.data_inicio.strftime('%d/%m/%Y')} das "
               f"{reserva.hora_inicio.strftime('%H:%M')} às "
               f"{reserva.hora_fim.strftime('%H:%M')} foi aprovada.")
        self._criar(
            reserva.solicitante,
            Notificacao.Tipo.RESERVA_APROVADA,
            '✅ Reserva Aprovada',
            msg, reserva
        )

    def notificar_rejeicao(self, reserva):
        msg = (f"Sua reserva para {reserva.sala.nome} em "
               f"{reserva.data_inicio.strftime('%d/%m/%Y')} foi rejeitada. "
               f"Motivo: {reserva.motivo_rejeicao or 'Não informado'}")
        self._criar(
            reserva.solicitante,
            Notificacao.Tipo.RESERVA_REJEITADA,
            '❌ Reserva Rejeitada',
            msg, reserva
        )

    def notificar_cancelamento(self, reserva):
        msg = (f"Sua reserva para {reserva.sala.nome} em "
               f"{reserva.data_inicio.strftime('%d/%m/%Y')} foi cancelada.")
        self._criar(
            reserva.solicitante,
            Notificacao.Tipo.RESERVA_CANCELADA,
            '🚫 Reserva Cancelada',
            msg, reserva
        )

    def notificar_override(self, reserva):
        msg = (f"ATENÇÃO: Sua reserva para {reserva.sala.nome} em "
               f"{reserva.data_inicio.strftime('%d/%m/%Y')} das "
               f"{reserva.hora_inicio.strftime('%H:%M')} às "
               f"{reserva.hora_fim.strftime('%H:%M')} foi substituída "
               f"por uma reserva administrativa. "
               f"Motivo: {reserva.motivo_override or 'Não informado'}")
        self._criar(
            reserva.solicitante,
            Notificacao.Tipo.RESERVA_OVERRIDE,
            '⚠️ Reserva Substituída',
            msg, reserva
        )

    def _criar(self, destinatario, tipo, titulo, mensagem, reserva=None):
        try:
            notif = Notificacao.objects.create(
                destinatario=destinatario,
                tipo=tipo,
                titulo=titulo,
                mensagem=mensagem,
                reserva=reserva,
            )
            # Tentar enviar e-mail de forma assíncrona
            self._enviar_email_async(notif)
            return notif
        except Exception as e:
            logger.error(f"Erro ao criar notificação: {e}")

    def _enviar_email_async(self, notificacao):
        """Envia e-mail via Celery (se disponível) ou de forma síncrona."""
        try:
            from apps.notificacoes.tasks import enviar_email_notificacao
            enviar_email_notificacao.delay(notificacao.pk)
        except Exception:
            # Fallback síncrono se Celery não disponível
            self._enviar_email_sync(notificacao)

    def _enviar_email_sync(self, notificacao):
        try:
            if notificacao.destinatario.email:
                send_mail(
                    subject=f"[IGC Salas] {notificacao.titulo}",
                    message=notificacao.mensagem,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[notificacao.destinatario.email],
                    fail_silently=True,
                )
                notificacao.email_enviado = True
                notificacao.save(update_fields=['email_enviado'])
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail: {e}")
