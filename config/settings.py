
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- НАСТРОЙКИ БЕЗОПАСНОСТИ И ОКРУЖЕНИЯ ---

# Ключ берется из переменной окружения. КРИТИЧЕСКИ ВАЖНО для продакшена.
SECRET_KEY = os.environ.get('SECRET_KEY')

# Режим DEBUG читается из переменной окружения.
# В .env.dev он True, в .env.prod он False.
# Выражение `os.environ.get('DEBUG') == 'True'` корректно обработает строки 'True' и 'False'
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
    'rest_framework.authtoken', # Для аутентификации по токену
    'django_filters',
    'drf_spectacular', # Для генерации Swagger/OpenAPI

    # Local apps
    'apps.users',
    'apps.network',
    'apps.api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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
    'SERVE_INCLUDE_SCHEMA': False, # Не показывать голую схему
}
