import os
import secrets
from pathlib import Path
from urllib.parse import urlsplit

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.environ.get('JOURNAL_ENV') == 'development'
DATA_DIR = BASE_DIR / 'data'
if DEBUG:
    DATA_DIR.mkdir(exist_ok=True)
    secret_file = DATA_DIR / '.secret-key'
    if not secret_file.exists():
        secret_file.write_text(secrets.token_urlsafe(64))
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') or secret_file.read_text().strip()
else:
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '')
    if len(SECRET_KEY) < 50:
        raise ImproperlyConfigured('Set DJANGO_SECRET_KEY to a random secret of at least 50 characters.')

PUBLIC_URL = os.environ.get('PUBLIC_URL', 'http://localhost:8001' if DEBUG else 'https://isack.space').rstrip('/')
ALLOWED_HOSTS = [urlsplit(PUBLIC_URL).hostname, 'localhost', '127.0.0.1']
if DEBUG:
    ALLOWED_HOSTS.append('testserver')
ALLOWED_HOSTS += [h.strip() for h in os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',') if h.strip()]
CSRF_TRUSTED_ORIGINS = [PUBLIC_URL]
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL:
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=60, conn_health_checks=True)}
elif DEBUG:
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': DATA_DIR / 'journal.sqlite3'}}
else:
    raise ImproperlyConfigured('Production requires DATABASE_URL pointing to PostgreSQL.')
if not DEBUG and DATABASES['default']['ENGINE'] != 'django.db.backends.postgresql':
    raise ImproperlyConfigured('Production requires PostgreSQL.')

INSTALLED_APPS = [
    'publishing',
    'wagtail.contrib.forms', 'wagtail.contrib.redirects', 'wagtail.contrib.settings',
    'wagtail.embeds', 'wagtail.sites', 'wagtail.users', 'wagtail.snippets',
    'wagtail.documents', 'wagtail.images', 'wagtail.search', 'wagtail.admin', 'wagtail',
    'modelcluster', 'taggit',
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'django.contrib.sitemaps', 'django_otp', 'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static', 'axes',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'publishing.middleware.RequireAdminOTP',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
    'axes.middleware.AxesMiddleware',
]
ROOT_URLCONF = 'journal.urls'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'], 'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request', 'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'publishing.context.journal_context',
    ]}}]
WSGI_APPLICATION = 'journal.wsgi.application'
AUTHENTICATION_BACKENDS = ['axes.backends.AxesStandaloneBackend', 'django.contrib.auth.backends.ModelBackend']
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1
AXES_LOCKOUT_PARAMETERS = [['username', 'ip_address']]
AXES_RESET_ON_SUCCESS = True
LANGUAGE_CODE = 'en'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STATIC_URL = '/cms-static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STORAGES = {'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
MEDIA_URL = '/media/'
MEDIA_ROOT = Path(os.environ.get('MEDIA_ROOT', BASE_DIR / 'media'))
WAGTAIL_SITE_NAME = 'Side notes Studio'
WAGTAILADMIN_BASE_URL = PUBLIC_URL
WAGTAILIMAGES_MAX_UPLOAD_SIZE = 15 * 1024 * 1024
WAGTAILIMAGES_MAX_IMAGE_PIXELS = 40_000_000
WAGTAILIMAGES_EXTENSIONS = ['avif', 'gif', 'jpg', 'jpeg', 'png', 'webp']
WAGTAILIMAGES_JPEG_QUALITY = 85
WAGTAILIMAGES_WEBP_QUALITY = 85
WAGTAILIMAGES_AVIF_QUALITY = 65
WAGTAILADMIN_USER_LOGIN_FORM = 'wagtail.admin.forms.auth.LoginForm'
WAGTAIL_ENABLE_UPDATE_CHECK = False
WAGTAIL_PASSWORD_RESET_ENABLED = True
LOGIN_URL = '/admin/login/'
# Allow the bounded MCP JSON envelope for a base64 image up to 2 MiB.
DATA_UPLOAD_MAX_MEMORY_SIZE = 3_000_000
SESSION_COOKIE_NAME = 'journal_session'
CSRF_COOKIE_NAME = 'journal_csrf'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 8 * 60 * 60
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = not DEBUG
SECURE_REDIRECT_EXEMPT = [r'^healthz$']
SECURE_HSTS_SECONDS = 31_536_000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS = 'SAMEORIGIN'
OTP_TOTP_ISSUER = 'Side notes Studio'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' if os.environ.get('EMAIL_HOST') else ('django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.dummy.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'true').lower() == 'true'
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Isack Journal <noreply@isack.space>')
WAGTAIL_PASSWORD_RESET_ENABLED = DEBUG or bool(EMAIL_HOST)
PORTFOLIO_SITEMAP = Path(os.environ.get('PORTFOLIO_SITEMAP', BASE_DIR.parent / 'dist/sitemap.xml'))
LOGGING = {'version': 1, 'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': os.environ.get('JOURNAL_LOG_LEVEL', 'INFO')}}
