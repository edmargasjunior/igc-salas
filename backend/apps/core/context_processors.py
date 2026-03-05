"""Context processors globais."""
from django.conf import settings


def site_settings(request):
    """Injeta configurações do site em todos os templates."""
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'IGC Salas'),
        'SITE_URL': getattr(settings, 'SITE_URL', ''),
        'DEBUG': settings.DEBUG,
    }
