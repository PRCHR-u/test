import logging
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# Получаем логгер с именем 'security'
security_logger = logging.getLogger('security')


class UserManager(BaseUserManager):
    """
    Кастомный менеджер для модели User с логированием.
    """

    def create_user(self, username, email=None, password=None, **extra_fields):
        """
        Создает и сохраняет пользователя с логированием.
        """
        if not username:
            raise ValueError('The given username must be set')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        # Логируем событие
        security_logger.info(f"Пользователь '{user.username}' успешно создан.")
        
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """
        Создает и сохраняет суперпользователя с логированием.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user(username, email, password, **extra_fields)
        
        # Логируем событие создания суперпользователя
        security_logger.warning(f"Суперпользователь '{user.username}' успешно создан.")
        
        return user


class User(AbstractUser):
    """
    Кастомная модель пользователя.
    """
    # Убираем поле email из required, т.к. мы используем username для входа
    email = models.EmailField('email address', blank=True)
    
    # Подключаем наш кастомный менеджер
    objects = UserManager()
