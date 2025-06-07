from django.apps import AppConfig


class AgendamecanicaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agendamecanica'

    def ready(self):
        import agendamecanica.signals  # Importa os sinais ao iniciar o app