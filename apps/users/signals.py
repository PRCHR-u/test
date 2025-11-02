import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

# Получаем наш логгер безопасности
security_logger = logging.getLogger('security')


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Логирует успешный вход пользователя в систему."""
    ip_address = request.META.get('REMOTE_ADDR')
    security_logger.info(
        f"Пользователь '{user.username}' успешно вошел в систему с IP: {ip_address}"
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Логирует успешный выход пользователя из системы."""
    if user:  # Пользователь может быть None, если сессия истекла
        security_logger.info(f"Пользователь '{user.username}' вышел из системы.")


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """Логирует неудачную попытку входа в систему."""
    username = credentials.get('username')
    ip_address = request.META.get('REMOTE_ADDR')
    security_logger.warning(
        f"Неудачная попытка входа для пользователя '{username}' с IP: {ip_address}"
    )
