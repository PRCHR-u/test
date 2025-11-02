from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'

    def ready(self):
        """
        Этот метод вызывается, когда приложение готово.
        Мы импортируем сигналы здесь, чтобы они были зарегистрированы.
        """
        import apps.users.signals  # noqa
