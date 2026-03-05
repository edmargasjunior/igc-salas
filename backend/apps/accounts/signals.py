"""Signals de accounts."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Usuario


@receiver(post_save, sender=Usuario)
def criar_perfil_professor(sender, instance, created, **kwargs):
    """Cria perfil de professor automaticamente se o perfil for 'professor'."""
    if created and instance.perfil == Usuario.Perfil.PROFESSOR:
        try:
            from apps.academico.models import Professor
            if not Professor.objects.filter(usuario=instance).exists():
                Professor.objects.create(
                    usuario=instance,
                    siape=f"SIAPE-{instance.pk:06d}"
                )
        except Exception:
            pass
