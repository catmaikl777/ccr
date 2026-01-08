import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Production settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'd_)q(x8acik%p3@1+z*io3^y*2@9#^aow1^p!-py)u-$)@*ohd')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = ['*']  # Для бесплатного хостинга

ROOT_URLCONF = 'CATVID.urls'

# MongoDB Atlas (бесплатный) или локальный MongoDB
MONGO_URI = os.environ.get('DATABASE_URL') or os.environ.get('MONGODB_URL') or os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')

# Проверяем, если это MongoDB Atlas
if 'mongodb.net' in MONGO_URI:
    DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': 'clicker_game',
            'CLIENT': {
                'host': MONGO_URI,
                'ssl': True,
                'ssl_cert_reqs': 'CERT_NONE',
                'retryWrites': True,
                'w': 'majority',
            }
        }
    }
else:
    # Локальная база данных
    DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': 'clicker_game',
            'CLIENT': {
                'host': MONGO_URI,
            }
        }
    }

# Локальное кэширование в памяти
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'clicker-cache',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 10000,
        }
    }
}

# Стандартные сессии в БД
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# WebSocket через локальную память
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Database connection pool
DATABASE_POOL_ARGS = {
    'max_overflow': 10,
    'pool_size': 5,
    'recycle': 300,
}

# settings.py - добавить/проверить конфигурацию TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # или путь к вашим шаблонам
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

# Middleware с WhiteNoise для статики
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Для статики
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Статические файлы для production
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'main' / 'static',
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Медиа файлы (загружаемые пользователями)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# Убираем ManifestStaticFilesStorage для разработки
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Security для высоких нагрузок
# Отключаем избыточные HTTP-заголовки безопасности для разработки
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'

INSTALLED_APPS = [
    # Стандартные приложения Django (ОБЯЗАТЕЛЬНЫ в этом порядке):
    'django.contrib.admin',  # Админка
    'django.contrib.auth',  # Аутентификация
    'django.contrib.contenttypes',  # Content types
    'django.contrib.sessions',  # Сессии
    'django.contrib.messages',  # Сообщения
    'django.contrib.staticfiles',  # Статические файлы

    # Ваши приложения:
    'main',  # Ваше приложение с игрой
]

# Убираю ошибку с логами для Render
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         'battles': {
#             'handlers': ['console'],
#             'level': 'INFO',
#         },
#     },
# }