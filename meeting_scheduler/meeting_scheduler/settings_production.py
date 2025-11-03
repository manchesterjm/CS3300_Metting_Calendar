"""
Production settings for PythonAnywhere deployment

This file extends the base settings.py with production-specific configurations.
Use this settings file when deploying to PythonAnywhere.

IMPORTANT: Set DJANGO_SETTINGS_MODULE=meeting_scheduler.settings_production
in your WSGI file on PythonAnywhere.
"""

from .settings import *
import os

# Generate a new SECRET_KEY for production using:
# python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY = os.environ.get('SECRET_KEY', 'CHANGE-THIS-IN-PRODUCTION')

# SECURITY: Disable debug mode in production
DEBUG = False

# IMPORTANT: Update this with your PythonAnywhere username
# Example: ['johndoe.pythonanywhere.com', 'www.yourdomain.com']
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'YOUR_USERNAME.pythonanywhere.com').split(',')

# Database
# PythonAnywhere uses SQLite3 - works great for this application
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,  # Prevent database lock errors
        }
    }
}

# Email Configuration for PythonAnywhere
# Uses Gmail SMTP - requires Gmail App Password (not regular password)
# To generate app password:
# 1. Go to https://myaccount.google.com/security
# 2. Enable 2-Step Verification
# 3. Go to "App passwords"
# 4. Generate password for "Mail" / "Other"
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER', 'your-email@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'your-app-password-here')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER

# Static files (CSS, JavaScript, Images)
# Run: python manage.py collectstatic
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Media files (user uploads) - if you add file uploads later
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Security Settings for Production
# These ensure your app uses HTTPS and secure cookies
SECURE_SSL_REDIRECT = True  # Redirect HTTP to HTTPS
SESSION_COOKIE_SECURE = True  # Only send session cookie over HTTPS
CSRF_COOKIE_SECURE = True  # Only send CSRF cookie over HTTPS
SECURE_BROWSER_XSS_FILTER = True  # Enable browser XSS filtering
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME type sniffing
X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking

# HTTP Strict Transport Security (HSTS)
# Tells browsers to always use HTTPS
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session Security
SESSION_COOKIE_AGE = 3600  # 1 hour session timeout
SESSION_SAVE_EVERY_REQUEST = True  # Extend session on each request
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_COOKIE_SAMESITE = 'Strict'  # Prevent CSRF via cookies

# CSRF Security
CSRF_COOKIE_HTTPONLY = True  # Prevent JavaScript access to CSRF cookie
CSRF_COOKIE_SAMESITE = 'Strict'  # Prevent CSRF attacks

# Logging Configuration
# Logs errors to file for debugging production issues
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django_error.log',
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Caching Configuration (optional but recommended)
# Uses local memory cache for better performance
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'meeting-scheduler-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Admin Configuration
# Admins receive error emails (if configured)
ADMINS = [
    ('Admin', os.environ.get('ADMIN_EMAIL', 'admin@example.com')),
]
MANAGERS = ADMINS

# Time Zone
# Ensure this matches your expected timezone for meeting scheduling
USE_TZ = True
TIME_ZONE = 'UTC'  # Change to your timezone if needed (e.g., 'America/New_York')

# Internationalization
LANGUAGE_CODE = 'en-us'
USE_I18N = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Additional Security Headers
SECURE_REFERRER_POLICY = 'same-origin'

# Production-specific settings
# Disable browsable API if you add Django REST Framework later
# REST_FRAMEWORK = {
#     'DEFAULT_RENDERER_CLASSES': [
#         'rest_framework.renderers.JSONRenderer',
#     ]
# }

# PythonAnywhere-specific notes:
# - PythonAnywhere provides HTTPS by default
# - Static files are served via PythonAnywhere's static files mapping
# - Database backups should be done manually (see DEPLOYMENT_PYTHONANYWHERE.md)
# - Monitor logs at ~/CS3300_Metting_Calendar/meeting_scheduler/logs/
