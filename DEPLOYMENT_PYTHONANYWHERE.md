# PythonAnywhere Deployment Guide

Complete guide for deploying the Meeting Scheduler Django application to PythonAnywhere.

## Overview

**Platform**: PythonAnywhere (https://www.pythonanywhere.com)
**Plan**: Hacker Plan ($5/month)
**Django Version**: 5.1.13
**Python Version**: 3.13
**Database**: SQLite (included)
**Email**: SMTP via Gmail or PythonAnywhere's mail server

---

## Pre-Deployment Checklist

Before deploying, ensure:

- ✅ All tests passing locally (153/153 tests)
- ✅ Pylint score: 10.00/10
- ✅ Security scans completed (0 vulnerabilities)
- ✅ Code pushed to GitHub repository
- ✅ Gmail account or email service credentials ready
- ✅ requirements.txt file up to date
- ✅ Production settings prepared

---

## Step 1: PythonAnywhere Account Setup

### 1.1 Sign Up for PythonAnywhere

1. Go to https://www.pythonanywhere.com
2. Click "Pricing & signup"
3. Select "Hacker Plan" ($5/month)
4. Create account with email/password
5. Verify email address

### 1.2 Account Configuration

**Included with Hacker Plan:**
- Custom domain support (optional, $1/month extra)
- SSH access (for Git operations)
- Always-on web app
- 512 MB RAM
- 100k CPU seconds/day
- SMTP email support

---

## Step 2: Deploy Django Application

### 2.1 Open Bash Console

1. Log into PythonAnywhere dashboard
2. Click "Consoles" tab
3. Click "Bash" to start a new console

### 2.2 Clone Repository

```bash
# Clone your repository
git clone https://github.com/manchesterjm/CS3300_Metting_Calendar.git
cd CS3300_Metting_Calendar/meeting_scheduler

# Verify code is present
ls -la
```

### 2.3 Create Virtual Environment

```bash
# Create virtual environment with Python 3.13
mkvirtualenv --python=/usr/bin/python3.13 meeting_scheduler

# Activate virtual environment (should auto-activate)
workon meeting_scheduler
```

### 2.4 Install Dependencies

```bash
# Install Django and dependencies
pip install django==5.1.13
pip install beautifulsoup4
pip install requests

# Or install from requirements.txt
pip install -r requirements.txt

# Verify installation
python -c "import django; print(django.get_version())"
```

---

## Step 3: Configure Web App

### 3.1 Create Web App

1. Go to "Web" tab in PythonAnywhere dashboard
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select "Python 3.13"
5. Click "Next"

### 3.2 Configure WSGI File

1. On the Web tab, find "Code" section
2. Click on WSGI configuration file link
3. Delete existing content
4. Add the following configuration:

```python
# /var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py

import os
import sys

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/CS3300_Metting_Calendar/meeting_scheduler'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variable to tell Django where settings are
os.environ['DJANGO_SETTINGS_MODULE'] = 'meeting_scheduler.settings'

# Activate your virtual environment
activate_this = '/home/YOUR_USERNAME/.virtualenvs/meeting_scheduler/bin/activate_this.py'
exec(open(activate_this).read(), {'__file__': activate_this})

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**IMPORTANT**: Replace `YOUR_USERNAME` with your actual PythonAnywhere username.

### 3.3 Configure Virtual Environment Path

1. On Web tab, find "Virtualenv" section
2. Enter path to virtual environment:
   ```
   /home/YOUR_USERNAME/.virtualenvs/meeting_scheduler
   ```
3. Click checkmark to save

### 3.4 Configure Source Code Path

1. On Web tab, find "Code" section
2. Click "Source code" link
3. Enter path:
   ```
   /home/YOUR_USERNAME/CS3300_Metting_Calendar/meeting_scheduler
   ```

---

## Step 4: Production Settings Configuration

### 4.1 Create Production Settings File

Create a new file `meeting_scheduler/settings_production.py`:

```python
"""
Production settings for PythonAnywhere deployment
"""
from .settings import *
import os

# SECURITY WARNING: keep the secret key used in production secret!
# Generate a new secret key for production
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'GENERATE-A-NEW-SECRET-KEY-HERE')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# IMPORTANT: Add your PythonAnywhere domain
ALLOWED_HOSTS = [
    'YOUR_USERNAME.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
]

# Database
# PythonAnywhere uses SQLite by default - works great for this app
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email Configuration for PythonAnywhere
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER', 'your-email@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'your-app-password')
DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_USER', 'your-email@gmail.com')

# Static files configuration
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Security settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django_error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

### 4.2 Update WSGI to Use Production Settings

Update your WSGI file to use production settings:

```python
# In WSGI file, change this line:
os.environ['DJANGO_SETTINGS_MODULE'] = 'meeting_scheduler.settings_production'
```

### 4.3 Generate Secret Key

Generate a new SECRET_KEY for production:

```bash
# In PythonAnywhere Bash console
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and paste into `settings_production.py`.

---

## Step 5: Configure Email (Gmail)

### 5.1 Set Up Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Click "Security" in left sidebar
3. Enable 2-Step Verification (if not already enabled)
4. Go back to Security settings
5. Click "App passwords"
6. Select "Mail" and "Other (Custom name)"
7. Enter "PythonAnywhere Django App"
8. Click "Generate"
9. **Save the 16-character password** (you'll need this)

### 5.2 Set Environment Variables

PythonAnywhere doesn't have built-in environment variables, so use one of these methods:

**Option A: Create .env file (Recommended)**

```bash
# In your project directory
cd ~/CS3300_Metting_Calendar/meeting_scheduler
nano .env
```

Add:
```bash
DJANGO_SECRET_KEY=your-generated-secret-key-here
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
```

Install python-decouple:
```bash
pip install python-decouple
```

Update `settings_production.py`:
```python
from decouple import config

SECRET_KEY = config('DJANGO_SECRET_KEY')
EMAIL_HOST_USER = config('EMAIL_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_PASSWORD')
```

**Option B: Set in settings file directly (Less secure)**

Edit `settings_production.py` directly with credentials (not recommended for public repos).

---

## Step 6: Database Setup

### 6.1 Create Logs Directory

```bash
cd ~/CS3300_Metting_Calendar/meeting_scheduler
mkdir logs
```

### 6.2 Run Migrations

```bash
# Make sure you're in the virtual environment
workon meeting_scheduler

# Navigate to project directory
cd ~/CS3300_Metting_Calendar/meeting_scheduler

# Run migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
# Follow prompts to set username, email, password
```

### 6.3 Collect Static Files

```bash
python manage.py collectstatic --noinput
```

---

## Step 7: Configure Static Files

### 7.1 Set Static Files Path in PythonAnywhere

1. Go to "Web" tab
2. Find "Static files" section
3. Add mapping:
   - **URL**: `/static/`
   - **Directory**: `/home/YOUR_USERNAME/CS3300_Metting_Calendar/meeting_scheduler/staticfiles`
4. Click checkmark to save

### 7.2 Verify Static Files

```bash
# Check that static files were collected
ls -la ~/CS3300_Metting_Calendar/meeting_scheduler/staticfiles
```

---

## Step 8: Reload and Test

### 8.1 Reload Web App

1. Go to "Web" tab
2. Click green "Reload" button at the top
3. Wait for reload to complete

### 8.2 Test Application

1. Visit your site: `https://YOUR_USERNAME.pythonanywhere.com`
2. Test features:
   - ✅ Home page loads
   - ✅ Registration works
   - ✅ Login works
   - ✅ Calendar view works
   - ✅ Add unavailability works
   - ✅ Group features work
   - ✅ Admin panel accessible at `/admin/`

### 8.3 Test Email

1. Go to password reset page: `/password-reset/`
2. Enter your email
3. Check email inbox for reset link
4. Verify email was received

---

## Step 9: Monitoring and Maintenance

### 9.1 View Error Logs

**Web App Error Log:**
1. Go to "Web" tab
2. Click "Log files" links
3. View error.log and server.log

**Django Error Log:**
```bash
# In Bash console
tail -f ~/CS3300_Metting_Calendar/meeting_scheduler/logs/django_error.log
```

### 9.2 Update Code

To update your deployed code:

```bash
# In Bash console
cd ~/CS3300_Metting_Calendar
git pull origin main

# If requirements changed
workon meeting_scheduler
pip install -r meeting_scheduler/requirements.txt

# If models changed
cd meeting_scheduler
python manage.py migrate

# Collect static files if changed
python manage.py collectstatic --noinput

# Then reload web app in Web tab
```

### 9.3 Database Backup

```bash
# Backup database
cd ~/CS3300_Metting_Calendar/meeting_scheduler
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d)

# Download backup (use "Files" tab in PythonAnywhere)
```

---

## Step 10: Custom Domain (Optional)

### 10.1 Add Custom Domain

If you want to use your own domain (costs extra $1/month):

1. Go to "Web" tab
2. Click "Add a new web app"
3. Enter your custom domain
4. Follow DNS configuration instructions

### 10.2 Update ALLOWED_HOSTS

Add your custom domain to `settings_production.py`:

```python
ALLOWED_HOSTS = [
    'YOUR_USERNAME.pythonanywhere.com',
    'yourdomain.com',
    'www.yourdomain.com',
]
```

---

## Troubleshooting

### Issue: 502 Bad Gateway

**Cause**: WSGI configuration error or virtual environment not activated

**Solution**:
1. Check WSGI file has correct paths
2. Verify virtual environment path is correct
3. Check error log for Python tracebacks
4. Reload web app

### Issue: Static Files Not Loading

**Cause**: Static files not collected or incorrect path

**Solution**:
```bash
python manage.py collectstatic --noinput
```

Verify static files mapping in Web tab matches collected files location.

### Issue: Email Not Sending

**Cause**: Gmail app password incorrect or 2FA not enabled

**Solution**:
1. Verify Gmail app password is correct
2. Check EMAIL_HOST_USER and EMAIL_PASSWORD in settings
3. Test with Django shell:
```python
python manage.py shell
from django.core.mail import send_mail
send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

### Issue: Database Lock Errors

**Cause**: SQLite concurrent access (rare with this app)

**Solution**:
```python
# In settings_production.py, add:
DATABASES['default']['OPTIONS'] = {
    'timeout': 20,
}
```

### Issue: CSRF Verification Failed

**Cause**: CSRF_COOKIE_SECURE=True but using HTTP

**Solution**:
PythonAnywhere provides HTTPS by default. If testing locally with HTTP, temporarily set:
```python
CSRF_COOKIE_SECURE = False  # Only for local testing
```

### Issue: DisallowedHost Error

**Cause**: Domain not in ALLOWED_HOSTS

**Solution**:
Add your PythonAnywhere domain to `settings_production.py`:
```python
ALLOWED_HOSTS = ['YOUR_USERNAME.pythonanywhere.com']
```

---

## Cost Breakdown

**PythonAnywhere Hacker Plan**: $5/month
- Includes web app hosting
- 512 MB RAM
- SMTP email support
- Custom domain support (optional +$1/month)

**Total Monthly Cost**: $5/month (or $6/month with custom domain)

**Free Alternatives for Testing:**
- PythonAnywhere Free Plan (limited, sleeps after inactivity)

---

## Performance Optimization

### Enable Caching

Add to `settings_production.py`:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

### Database Optimization

Already using `select_related()` and `prefetch_related()` for N+1 query prevention (see AI_CODE_REVIEW_FIXES.md #15).

---

## Security Checklist

Before going live, verify:

- ✅ DEBUG = False
- ✅ SECRET_KEY is unique and not in version control
- ✅ ALLOWED_HOSTS configured correctly
- ✅ SECURE_SSL_REDIRECT = True
- ✅ SESSION_COOKIE_SECURE = True
- ✅ CSRF_COOKIE_SECURE = True
- ✅ All security headers configured
- ✅ Admin account has strong password
- ✅ Email credentials stored securely (not in code)
- ✅ Security scans completed (Bandit, pip-audit)

---

## Post-Deployment Testing

After deployment, test all features:

### Authentication
- ✅ User registration
- ✅ Login/logout
- ✅ Password reset email
- ✅ Account management

### Calendar Features
- ✅ Add unavailability
- ✅ View unavailability list
- ✅ Show free times
- ✅ Show last five entries
- ✅ Delete entries

### Group Features
- ✅ Create group
- ✅ Add members
- ✅ View group calendar
- ✅ Show common free times

### Admin Features
- ✅ Admin login at /admin/
- ✅ View users
- ✅ View unavailability entries
- ✅ Password generation feature

---

## Support and Resources

**PythonAnywhere Help:**
- Documentation: https://help.pythonanywhere.com/
- Forums: https://www.pythonanywhere.com/forums/
- Email Support: support@pythonanywhere.com

**Django Documentation:**
- Deployment: https://docs.djangoproject.com/en/5.1/howto/deployment/
- Security: https://docs.djangoproject.com/en/5.1/topics/security/

**Project Documentation:**
- CLAUDE.md - Development guide
- STYLE_GUIDE.md - Code standards
- SECURITY_GUIDE.md - Security practices
- AI_CODE_REVIEW_FIXES.md - Code review findings

---

## Quick Reference Commands

```bash
# Activate virtual environment
workon meeting_scheduler

# Update code from Git
cd ~/CS3300_Metting_Calendar
git pull origin main

# Run migrations
cd meeting_scheduler
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell

# View error logs
tail -f ~/CS3300_Metting_Calendar/meeting_scheduler/logs/django_error.log

# Backup database
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d)
```

**After any code/settings changes**: Go to Web tab and click "Reload" button.

---

## Next Steps After Deployment

1. ✅ Test all features thoroughly
2. ✅ Set up database backup schedule
3. ✅ Monitor error logs for first week
4. ✅ Add custom domain (optional)
5. ✅ Document production URL for users
6. ✅ Consider adding meeting proposal feature (Phase 1)

---

**Last Updated**: 2025-11-03
**Django Version**: 5.1.13
**Python Version**: 3.13
**Platform**: PythonAnywhere Hacker Plan ($5/month)
