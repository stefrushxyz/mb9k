from django.apps import AppConfig
from django.contrib.auth.apps import AuthConfig

class AppConfig(AppConfig):
    name = 'app'
    verbose_name = 'App'

    def ready(self):
        import app.signals

class AuthConfig(AuthConfig):
    verbose_name = 'Auth'

