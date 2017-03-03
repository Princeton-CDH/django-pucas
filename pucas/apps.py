from django.apps import AppConfig


class PucasConfig(AppConfig):
    name = 'pucas'

    def ready(self):
        import pucas.signals
