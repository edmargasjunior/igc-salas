"""Signals para envio automático de notificações."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Reserva, LogReserva


@receiver(post_save, sender=Reserva)
def criar_log_reserva(sender, instance, created, **kwargs):
    """Cria log automático para cada mudança de status."""
    if created:
        LogReserva.objects.create(
            reserva=instance,
            usuario=instance.solicitante,
            acao=LogReserva.Acao.CRIADA,
            descricao=f"Reserva criada para {instance.sala} em {instance.data_inicio} {instance.hora_inicio}-{instance.hora_fim}",
        )


@receiver(post_save, sender=Reserva)
def notificar_mudanca_status(sender, instance, created, **kwargs):
    """Envia notificação quando status da reserva muda."""
    if created:
        return

    from apps.notificacoes.services import NotificacaoService
    service = NotificacaoService()

    if instance.status == Reserva.Status.APROVADA:
        service.notificar_aprovacao(instance)
    elif instance.status == Reserva.Status.REJEITADA:
        service.notificar_rejeicao(instance)
    elif instance.status == Reserva.Status.CANCELADA:
        service.notificar_cancelamento(instance)
    elif instance.status == Reserva.Status.SUBSTITUIDA:
        service.notificar_override(instance)
