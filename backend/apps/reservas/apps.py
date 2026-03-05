from django.apps import AppConfig
class ReservasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reservas'
    verbose_name = 'Reservas'
    def ready(self):
        import apps.reservas.signals
