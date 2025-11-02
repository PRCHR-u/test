
import os
from pathlib import Path # Используем pathlib для современного управления путями

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).resolve().parent.parent


# --- НАСТРОЙКИ БЕЗОПАСНОСТИ И ОКРУЖЕНИЯ ---

# Ключ берется из переменной окружения. КРИТИЧЕСКИ ВАЖНО для продакшена.
SECRET_KEY = os.environ.get('SECRET_KEY')

# Режим DEBUG читается из переменной окружения.
# В .env.dev он True, в .env.prod он False.
DEBUG = os.environ.get('DEBUG') == 'True'

# ALLOWED_HOSTS настраивается в зависимости от окружения
if DEBUG:
    # В режиме разработки разрешаем все хосты
    ALLOWED_HOSTS = ['*']
else:
    # В продакшене следует указать конкретный домен
    ALLOWED_HOSTS = ['your-production-domain.com', 'localhost', '127.0.0.1']

# --- КОНЕЦ НАСТРОЕК БЕЗОПАСНОСТИ ---


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'drf_spectacular',
    'corsheaders',  # для CORS

    # Local apps
    'apps.core', # Для менеджмент-команд
    'apps.users.apps.UsersConfig', # для поддержки сигналов
    'apps.network',
    'apps.api',
    'health', # приложение для мониторинга
]

MIDDLEWARE = [
    # middleware для логирования запросов должно быть первым
    'config.middleware.RequestLoggingMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'health.middleware.MetricsMiddleware', # Middleware для сбора метрик
]

# --- НАСТРОЙКИ CORS ---
# Источник: переменная окружения, содержащая домены через запятую.
# Например: "http://localhost:3000,http://127.0.0.1:3000"
CORS_ALLOWED_ORIGINS_STR = os.environ.get('CORS_ALLOWED_ORIGINS_STR', '')
CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS_STR.split(',') if CORS_ALLOWED_ORIGINS_STR else []

# Если в режиме разработки список пуст, разрешаем стандартные порты фронтенда
if DEBUG and not CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173", # Стандартный порт Vite/React
        "http://127.0.0.1:5173",
    ]

# --- КОНЕЦ НАСТРОЕК CORS ---


ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PGDATABASE'),
        'USER': os.environ.get('PGUSER'),
        'PASSWORD': os.environ.get('PGPASSWORD'),
        'HOST': os.environ.get('PGHOST'),
        'PORT': os.environ.get('PGPORT'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User model
AUTH_USER_MODEL = 'users.User'

# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}

# DRF Spectacular settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Electronics Network API',
    'DESCRIPTION': 'API для управления сетью поставщиков электроники. Сгенерировано с помощью Gemini.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# --- LOGGING CONFIGURATION ---

LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {asctime} {message}',
            'style': '{',
        },
        'json': {
            'format': '{\"timestamp\": \"%(asctime)s\", \"level\": \"%(levelname)s\", \"module\": \"%(module)s\", \"message\": \"%(message)s\"}',
        },
    },
    
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file_general': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'django.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'file_security': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'security.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'file_business': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'business.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'file_errors': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'errors.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'file_metrics': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'metrics.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'json',  # JSON формат для легкого парсинга
        },
    },
    
    'loggers': {
        'django': {
            'handlers': ['console', 'file_general', 'file_errors'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file_errors'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file_security'],
            'level': 'INFO',
            'propagate': False,
        },
        'security': {
            'handlers': ['file_security', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'business': {
            'handlers': ['file_business', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file_general'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'health': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },
        'metrics': {
            'handlers': ['console', 'file_metrics'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    
    'root': {
        'handlers': ['console', 'file_general', 'file_errors'],
        'level': 'INFO',
    },
}
