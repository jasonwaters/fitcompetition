from django.apps import AppConfig


class FitAppConfig(AppConfig):
    name = 'fitcompetition'
    verbose_name = "Fit Crown Application"

    def ready(self):
        import signals
