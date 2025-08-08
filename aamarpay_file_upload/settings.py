from pathlib import Path
import environ
import os
from datetime import timedelta

BASE_DIR_2 = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment Configuration
env = environ.Env(
    DEBUG=(bool, False),
    BCRYPT_ROUNDS=(int, 12),
    SESSION_COOKIE_SECURE=(bool, False),
    CSRF_COOKIE_SECURE=(bool, False),
    SECURE_SSL_REDIRECT=(bool, False),
    FILE_UPLOAD_MAX_SIZE=(int, 10485760),
    DATA_UPLOAD_MAX_SIZE=(int, 10485760),
    API_PAGE_SIZE=(int, 10),
    SECURE_BROWSER_XSS_FILTER=(bool, False),
    SECURE_CONTENT_TYPE_NOSNIFF=(bool, False),
    CACHE_TIMEOUT=(int, 300),
)

# Read environment file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Core Django Settings
SECRET_KEY = env('DJ_SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list("DJ_ALLOWED_HOSTS", default=[])

# Security Settings
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE')
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE') 
SECURE_SSL_REDIRECT = env('SECURE_SSL_REDIRECT')
SECURE_BROWSER_XSS_FILTER = env('SECURE_BROWSER_XSS_FILTER')
SECURE_CONTENT_TYPE_NOSNIFF = env('SECURE_CONTENT_TYPE_NOSNIFF')
X_FRAME_OPTIONS = env('X_FRAME_OPTIONS', default='DENY')

# CORS Configuration
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_ALL_ORIGINS = False
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# Application Definition
PREINSTALLED_APPS = [
    "corsheaders",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "debug_toolbar",
    "rest_framework",
    'rest_framework.authtoken',
    'django_extensions',
    'django_celery_beat',
]

DJ_APPS = [
    "payments",
    "uploads", 
    "authentication",
]

INSTALLED_APPS = PREINSTALLED_APPS + DJ_APPS

# Password Hashers (with configurable BCrypt rounds)
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

# BCrypt Configuration
BCRYPT_ROUNDS = env('BCRYPT_ROUNDS')

# Middleware Configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Debug Toolbar (only in debug mode)
if DEBUG:
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1']

ROOT_URLCONF = 'aamarpay_file_upload.urls'

# Templates Configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'aamarpay_file_upload' / 'Templates',
        ],
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

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': env('API_PAGE_SIZE'),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': env('ANON_RATE_LIMIT', default='100/hour'),
        'user': env('USER_RATE_LIMIT', default='1000/hour')
    },
}

WSGI_APPLICATION = 'aamarpay_file_upload.wsgi.application'

# Database Configuration
DATABASES = {
    "default": {
        "ENGINE": env("POSTGRES_ENGINE"),
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
    }
}

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = env('LANGUAGE_CODE', default='en-us')
TIME_ZONE = env('TIME_ZONE', default='Asia/Dhaka')
USE_I18N = True
USE_TZ = True

# Static Files Configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

# Authentication URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Media Files Configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery Configuration
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {}

# aamarPay Configuration
AAMARPAY_STORE_ID = env('AAMARPAY_STORE_ID')
AAMARPAY_SIGNATURE_KEY = env('AAMARPAY_SIGNATURE_KEY')
AAMARPAY_SANDBOX_URL = env('AAMARPAY_SANDBOX_URL')
AAMARPAY_SUCCESS_URL = env('AAMARPAY_SUCCESS_URL')
AAMARPAY_FAIL_URL = env('AAMARPAY_FAIL_URL')
AAMARPAY_CANCEL_URL = env('AAMARPAY_CANCEL_URL')

# File Upload Configuration
FILE_UPLOAD_MAX_MEMORY_SIZE = env('FILE_UPLOAD_MAX_SIZE')
DATA_UPLOAD_MAX_MEMORY_SIZE = env('DATA_UPLOAD_MAX_SIZE')
ALLOWED_FILE_EXTENSIONS = env.list('ALLOWED_FILE_EXTENSIONS', default=['.txt', '.docx'])

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': env('CACHE_BACKEND', default='django.core.cache.backends.locmem.LocMemCache'),
        'LOCATION': env('CACHE_LOCATION', default='unique-snowflake'),
        'TIMEOUT': env('CACHE_TIMEOUT'),
    }
}

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': env('LOG_LEVEL', default='DEBUG'),
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': True,
        },
        'payments': {
            'handlers': ['file', 'console'],
            'level': env('LOG_LEVEL', default='DEBUG'),
            'propagate': True,
        },
        'uploads': {
            'handlers': ['file', 'console'],
            'level': env('LOG_LEVEL', default='DEBUG'),
            'propagate': True,
        },
    },
}

# Create logs directory if it doesn't exist
LOG_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Production Security Settings (only apply in production)
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"