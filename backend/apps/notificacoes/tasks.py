"""Tasks Celery para notificações."""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger('apps.notificacoes')


@shared_task(bind=True, max_retries=3)
def enviar_email_notificacao(self, notificacao_id):
    """Task assíncrona para envio de e-mail de notificação."""
    from .models import Notificacao
    try:
        notif = Notificacao.objects.get(pk=notificacao_id)
        if notif.email_enviado:
            return
        if not notif.destinatario.email:
            return

        send_mail(
            subject=f"[IGC Salas] {notif.titulo}",
            message=notif.mensagem,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notif.destinatario.email],
            fail_silently=False,
        )
        notif.email_enviado = True
        notif.save(update_fields=['email_enviado'])
        logger.info(f"E-mail enviado para {notif.destinatario.email}")

    except Exception as exc:
        logger.error(f"Erro ao enviar e-mail notificacao #{notificacao_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)
