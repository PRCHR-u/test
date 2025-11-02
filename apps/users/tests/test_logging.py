import logging
from io import StringIO
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

# Перенастраиваем логирование для тестов, чтобы захватывать вывод в переменную
TEST_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'string_io': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'security': {
            'handlers': ['string_io'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


@override_settings(LOGGING=TEST_LOGGING)
class AuthLoggingSignalTests(TestCase):

    def setUp(self):
        """Создаем пользователя и настраиваем перехват логов."""
        self.log_stream = StringIO()
        # Получаем логгер 'security' и добавляем наш обработчик
        self.security_logger = logging.getLogger('security')
        self.handler = logging.StreamHandler(self.log_stream)
        self.security_logger.addHandler(self.handler)
        self.security_logger.setLevel(logging.INFO)

        self.username = "testuser"
        self.password = "strong-password-123"
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def tearDown(self):
        """Убираем наш обработчик, чтобы не мешать другим тестам."""
        self.security_logger.removeHandler(self.handler)

    def test_successful_login_is_logged(self):
        """Тестируем, что успешный вход логируется."""
        self.client.login(username=self.username, password=self.password)
        log_content = self.log_stream.getvalue()
        self.assertIn(f"Пользователь '{self.username}' успешно вошел в систему", log_content)

    def test_failed_login_is_logged(self):
        """Тестируем, что неудачный вход логируется."""
        # Используем встроенный url для входа в админку, чтобы сгенерировать сигнал
        self.client.post(reverse('admin:login'), {'username': self.username, 'password': 'wrongpassword'})
        log_content = self.log_stream.getvalue()
        self.assertIn(f"Неудачная попытка входа для пользователя '{self.username}'", log_content)
