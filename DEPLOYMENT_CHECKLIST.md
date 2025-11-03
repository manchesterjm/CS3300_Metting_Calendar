# PythonAnywhere Deployment Checklist

Quick reference checklist for deploying to PythonAnywhere. See DEPLOYMENT_PYTHONANYWHERE.md for detailed instructions.

## Pre-Deployment

- [ ] All tests passing locally (153/153 tests)
- [ ] Pylint score: 10.00/10
- [ ] Security scans completed (0 vulnerabilities)
- [ ] Code committed and pushed to GitHub
- [ ] Gmail account setup with app password
- [ ] PythonAnywhere account created ($5/month Hacker Plan)

## Initial Setup on PythonAnywhere

### 1. Clone Repository
- [ ] Open Bash console on PythonAnywhere
- [ ] Clone repository: `git clone https://github.com/manchesterjm/CS3300_Metting_Calendar.git`
- [ ] Navigate to project: `cd CS3300_Metting_Calendar/meeting_scheduler`

### 2. Create Virtual Environment
- [ ] Create virtualenv: `mkvirtualenv --python=/usr/bin/python3.13 meeting_scheduler`
- [ ] Activate: `workon meeting_scheduler`
- [ ] Install dependencies: `pip install -r requirements.txt`

### 3. Configure Web App
- [ ] Go to "Web" tab in PythonAnywhere dashboard
- [ ] Click "Add a new web app"
- [ ] Select "Manual configuration" + "Python 3.13"
- [ ] Configure WSGI file (see DEPLOYMENT_PYTHONANYWHERE.md Step 3.2)
- [ ] Set virtualenv path: `/home/YOUR_USERNAME/.virtualenvs/meeting_scheduler`
- [ ] Set source code path: `/home/YOUR_USERNAME/CS3300_Metting_Calendar/meeting_scheduler`

### 4. Production Settings
- [ ] Generate new SECRET_KEY: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- [ ] Update `settings_production.py` with SECRET_KEY
- [ ] Update ALLOWED_HOSTS with your PythonAnywhere domain
- [ ] Update WSGI file to use: `os.environ['DJANGO_SETTINGS_MODULE'] = 'meeting_scheduler.settings_production'`

### 5. Email Configuration
- [ ] Get Gmail app password (https://myaccount.google.com/security)
- [ ] Create `.env` file from `.env.example`
- [ ] Add EMAIL_USER and EMAIL_PASSWORD to `.env`
- [ ] Update `settings_production.py` email settings

### 6. Database Setup
- [ ] Create logs directory: `mkdir logs`
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Collect static files: `python manage.py collectstatic --noinput`

### 7. Static Files Configuration
- [ ] Go to "Web" tab on PythonAnywhere
- [ ] Add static files mapping:
  - URL: `/static/`
  - Directory: `/home/YOUR_USERNAME/CS3300_Metting_Calendar/meeting_scheduler/staticfiles`

### 8. Test Deployment
- [ ] Click "Reload" button on Web tab
- [ ] Visit: `https://YOUR_USERNAME.pythonanywhere.com`
- [ ] Test registration
- [ ] Test login
- [ ] Test calendar features
- [ ] Test email (password reset)
- [ ] Test admin panel: `/admin/`

## Post-Deployment Verification

### Functionality Tests
- [ ] User registration works
- [ ] Login/logout works
- [ ] Password reset email received
- [ ] Add unavailability entry
- [ ] View unavailability list
- [ ] Show free times
- [ ] Delete entries
- [ ] Create group
- [ ] Add group members
- [ ] View group calendar
- [ ] Show common free times

### Security Checks
- [ ] DEBUG = False
- [ ] SECRET_KEY is unique and secure
- [ ] ALLOWED_HOSTS configured correctly
- [ ] HTTPS enabled (automatic on PythonAnywhere)
- [ ] SESSION_COOKIE_SECURE = True
- [ ] CSRF_COOKIE_SECURE = True
- [ ] Admin panel accessible only to staff
- [ ] Email credentials not in code

### Performance Checks
- [ ] Static files loading correctly
- [ ] Pages load in < 2 seconds
- [ ] No database lock errors
- [ ] No 500 errors in logs

## Optional: Custom Domain (Cloudflare)

### Cloudflare Setup
- [ ] Register domain (e.g., syncmeet.com)
- [ ] Add domain to Cloudflare
- [ ] Configure DNS settings:
  - CNAME record: `@` → `YOUR_USERNAME.pythonanywhere.com`
  - CNAME record: `www` → `YOUR_USERNAME.pythonanywhere.com`
- [ ] Enable Cloudflare proxy (orange cloud)
- [ ] Enable SSL/TLS (Full mode)

### PythonAnywhere Custom Domain
- [ ] Go to "Web" tab
- [ ] Add custom domain ($1/month extra)
- [ ] Enter your domain: `yourdomain.com`
- [ ] Follow DNS instructions
- [ ] Wait for DNS propagation (up to 24 hours)

### Update Settings
- [ ] Add custom domain to ALLOWED_HOSTS in `settings_production.py`:
  ```python
  ALLOWED_HOSTS = [
      'YOUR_USERNAME.pythonanywhere.com',
      'yourdomain.com',
      'www.yourdomain.com',
  ]
  ```
- [ ] Reload web app

## Monitoring and Maintenance

### Daily/Weekly
- [ ] Check error logs: `/logs/django_error.log`
- [ ] Monitor web app status (should be "always on")
- [ ] Verify backup schedule

### Monthly
- [ ] Update Django: `pip install django --upgrade`
- [ ] Run security scans: `python run_security_scans.py`
- [ ] Check dependency vulnerabilities: `pip-audit`
- [ ] Backup database: `cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d)`

### As Needed
- [ ] Pull code updates: `git pull origin main`
- [ ] Run migrations if models changed: `python manage.py migrate`
- [ ] Collect static files if CSS/JS changed: `python manage.py collectstatic --noinput`
- [ ] Reload web app after changes

## Quick Commands Reference

```bash
# Activate virtual environment
workon meeting_scheduler

# Update code
cd ~/CS3300_Metting_Calendar
git pull origin main

# Run migrations
cd meeting_scheduler
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# View error logs
tail -f ~/CS3300_Metting_Calendar/meeting_scheduler/logs/django_error.log

# Backup database
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d)

# Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser
```

## Troubleshooting Quick Fixes

### 502 Bad Gateway
1. Check WSGI file paths
2. Verify virtualenv path
3. Check error log
4. Reload web app

### Static Files Not Loading
1. Run: `python manage.py collectstatic --noinput`
2. Verify static files mapping in Web tab
3. Reload web app

### Email Not Sending
1. Verify Gmail app password
2. Check EMAIL_HOST_USER and EMAIL_PASSWORD
3. Test with Django shell

### Database Locked
1. Check for long-running queries
2. Increase timeout in settings: `'timeout': 20`
3. Restart web app

## Support Resources

- **PythonAnywhere Help**: https://help.pythonanywhere.com/
- **Django Deployment**: https://docs.djangoproject.com/en/5.1/howto/deployment/
- **Project Docs**: DEPLOYMENT_PYTHONANYWHERE.md
- **Troubleshooting**: CLAUDE.md (Troubleshooting section)

---

**Cost**: $5/month (PythonAnywhere Hacker Plan) + optional $1/month (custom domain)
**Platform**: PythonAnywhere (https://www.pythonanywhere.com)
**Last Updated**: 2025-11-03
