# SendGrid Email Setup Guide

Complete guide for configuring SendGrid SMTP email service for the Meeting Scheduler Django application.

## Overview

**Service**: SendGrid (https://sendgrid.com)
**Cost**: FREE for up to 100 emails/day (forever)
**Use Case**: Password reset emails, email verification, system notifications
**Security**: Industry-standard TLS encryption, API key authentication

---

## Why SendGrid?

### Advantages Over Gmail

✅ **No Personal Email Required** - Create dedicated app email service
✅ **Professional Service** - Used by Uber, Airbnb, and thousands of companies
✅ **Better Deliverability** - Emails less likely to land in spam
✅ **100 Emails/Day Free** - Sufficient for password resets and verification
✅ **Analytics Dashboard** - Track email delivery and opens
✅ **API Key Authentication** - More secure than password-based auth
✅ **No 2FA Setup Required** - Simpler than Gmail app passwords

### Perfect For This Application

Your app sends emails for:
- Password reset requests
- Email verification (when users sign up)
- Account notifications

**Expected volume**: 5-50 emails/day → Well within free tier limits

---

## Part 1: SendGrid Account Setup (5 minutes)

### Step 1.1: Create Free Account

1. Go to https://sendgrid.com/free/
2. Click "Start for free" or "Try for free"
3. Fill out sign-up form:
   - **Email**: Use any email (your personal email is fine for setup)
   - **Password**: Create strong password
   - **Company name**: "Meeting Scheduler App" or your project name
4. Click "Create Account"

### Step 1.2: Verify Your Email

1. Check inbox for SendGrid verification email
2. Click verification link
3. Complete account setup survey (select relevant options):
   - **Email type**: Transactional emails
   - **Integration method**: SMTP Relay
   - **Programming language**: Python

### Step 1.3: Complete Onboarding

SendGrid will walk you through initial setup. You can skip the tutorial and proceed directly to configuration.

---

## Part 2: Sender Authentication (5 minutes)

Before sending emails, you must verify a sender email address.

### Step 2.1: Navigate to Sender Authentication

1. Log into SendGrid dashboard
2. Click **Settings** → **Sender Authentication** in left sidebar
3. You'll see two options:
   - **Domain Authentication** (advanced, requires DNS access)
   - **Single Sender Verification** (easy, recommended for this project)

### Step 2.2: Single Sender Verification (Recommended)

1. Click **"Get Started"** under "Single Sender Verification"
2. Click **"Create New Sender"**
3. Fill out the form:

**From Name**: `Meeting Scheduler` or `SyncMeet`
**From Email Address**: `noreply@yourdomain.com` or use a Gmail address you control
**Reply To**: Same as From Email (or your support email)
**Company Address**: Your address (required by anti-spam laws)
**City**: Your city
**State/Province**: Your state
**Zip Code**: Your zip code
**Country**: Your country

4. Click **"Create"**
5. Check your inbox for verification email
6. Click **"Verify Single Sender"** in the email

✅ **You can now send emails from this address!**

### Alternative: Domain Authentication (Advanced)

If you own a domain and want emails from `noreply@yourdomain.com`:

1. Click **"Get Started"** under "Domain Authentication"
2. Follow DNS configuration steps (requires adding DNS records)
3. This improves deliverability but is NOT required

**For this project, Single Sender Verification is sufficient.**

---

## Part 3: Create API Key (2 minutes)

### Step 3.1: Generate API Key

1. In SendGrid dashboard, click **Settings** → **API Keys**
2. Click **"Create API Key"** button (top right)
3. Fill out form:
   - **API Key Name**: `Django Meeting Scheduler` or `PythonAnywhere Production`
   - **API Key Permissions**: Select **"Restricted Access"**
4. Scroll down to **"Mail Send"** section
5. Toggle **"Mail Send"** to **"Full Access"** (this is the only permission needed)
6. Scroll to bottom and click **"Create & View"**

### Step 3.2: Save Your API Key

🚨 **CRITICAL**: The API key is shown **only once**!

```
SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

1. **Copy the entire key** (starts with `SG.`)
2. **Save it immediately** in a secure location (password manager or secure note)
3. Click **"Done"**

⚠️ **If you lose this key**, you'll need to create a new one.

---

## Part 4: Configure Django Settings (10 minutes)

### Step 4.1: Update Production Settings

Edit your production settings file (e.g., `meeting_scheduler/settings_production.py`):

```python
"""
Production settings for PythonAnywhere deployment
"""
from .settings import *
import os

# ... (existing settings) ...

# ============================================================
# EMAIL CONFIGURATION - SENDGRID
# ============================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'  # This is literally the string "apikey"
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com')
SERVER_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com')

# Email settings for password reset
EMAIL_TIMEOUT = 30  # Timeout in seconds
```

**Important Notes:**
- `EMAIL_HOST_USER` is literally the string `"apikey"` (not your actual key!)
- `EMAIL_HOST_PASSWORD` is your actual SendGrid API key (from environment variable)
- `DEFAULT_FROM_EMAIL` must match the email you verified in Step 2.2

### Step 4.2: Set Environment Variables

You have several options for setting environment variables on PythonAnywhere:

#### Option A: Using .env File (Recommended)

1. Install python-decouple:
```bash
pip install python-decouple
```

2. Create `.env` file in your project root:
```bash
cd ~/CS3300_Metting_Calendar/meeting_scheduler
nano .env
```

3. Add the following (replace with your actual values):
```bash
# SendGrid Configuration
SENDGRID_API_KEY=SG.your-actual-api-key-here
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Django Secret Key
DJANGO_SECRET_KEY=your-django-secret-key-here
```

4. Update `settings_production.py` to use python-decouple:
```python
from decouple import config

SECRET_KEY = config('DJANGO_SECRET_KEY')
EMAIL_HOST_PASSWORD = config('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
```

5. **Important**: Add `.env` to `.gitignore`:
```bash
echo ".env" >> .gitignore
```

#### Option B: Direct in Settings (Development Only)

For local testing (NEVER commit to Git):
```python
# settings.py (local development only)
EMAIL_HOST_PASSWORD = 'SG.your-actual-api-key-here'
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'
```

⚠️ **Never commit API keys to version control!**

---

## Part 5: Test Email Configuration (5 minutes)

### Step 5.1: Test Locally (Development)

Before deploying to PythonAnywhere, test email sending locally:

```bash
# Activate your virtual environment
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows

# Navigate to project directory
cd meeting_scheduler

# Start Django shell
python manage.py shell
```

In the Django shell:
```python
from django.core.mail import send_mail

# Test email
send_mail(
    subject='Test Email from Meeting Scheduler',
    message='This is a test email from your Django app using SendGrid!',
    from_email='noreply@yourdomain.com',  # Must match verified sender
    recipient_list=['your-personal-email@gmail.com'],  # Your email to receive test
    fail_silently=False,
)
```

**Expected output:**
```
1
```

This means 1 email was sent successfully!

### Step 5.2: Check Email Delivery

1. Check your personal email inbox
2. Look for email from "Meeting Scheduler" or your configured sender name
3. Check spam folder if not in inbox

✅ **If you received the email, SendGrid is configured correctly!**

### Step 5.3: Verify in SendGrid Dashboard

1. Go to SendGrid dashboard
2. Click **"Activity"** in left sidebar
3. You should see your test email in the activity feed
4. Click on it to see delivery details

---

## Part 6: Deploy to PythonAnywhere (5 minutes)

### Step 6.1: Install python-decouple on PythonAnywhere

```bash
# SSH into PythonAnywhere or use Bash console
workon meeting_scheduler
pip install python-decouple
```

### Step 6.2: Create .env File on PythonAnywhere

```bash
cd ~/CS3300_Metting_Calendar/meeting_scheduler
nano .env
```

Add your production credentials:
```bash
SENDGRID_API_KEY=SG.your-actual-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
DJANGO_SECRET_KEY=your-production-django-secret-key
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

### Step 6.3: Secure the .env File

```bash
# Make .env readable only by you
chmod 600 .env

# Verify permissions
ls -la .env
# Should show: -rw------- (owner read/write only)
```

### Step 6.4: Update WSGI Configuration

Your WSGI file should already be configured to use `settings_production.py`:

```python
# /var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py
os.environ['DJANGO_SETTINGS_MODULE'] = 'meeting_scheduler.settings_production'
```

### Step 6.5: Reload Web App

1. Go to PythonAnywhere **Web** tab
2. Click green **"Reload"** button at top
3. Wait for reload to complete

---

## Part 7: Test Production Email (5 minutes)

### Step 7.1: Test Password Reset Flow

1. Go to your deployed app: `https://YOUR_USERNAME.pythonanywhere.com`
2. Click **"Forgot Password?"** or go to `/password-reset/`
3. Enter your email address
4. Click **"Send Password Reset Email"**
5. Check your email inbox for password reset email

### Step 7.2: Verify Email Received

✅ Check for email from "Meeting Scheduler" or your configured sender
✅ Verify reset link works (click it and reset password)
✅ Verify email formatting looks professional

### Step 7.3: Check SendGrid Activity

1. Go to SendGrid dashboard → **Activity**
2. You should see the password reset email
3. Click on it to see delivery details:
   - **Delivered**: Email successfully sent
   - **Opens**: If user opened email (if open tracking enabled)
   - **Clicks**: If user clicked link

---

## Part 8: Monitoring and Troubleshooting

### Monitor Email Activity

**SendGrid Dashboard:**
1. Click **"Activity"** to see all sent emails
2. Click **"Stats"** to see delivery metrics
3. Monitor bounces and spam reports

**Daily Limit Tracking:**
- Free tier: 100 emails/day
- Resets at midnight UTC
- Check **Stats → Overview** for current usage

### Common Issues and Solutions

#### Issue: "Authentication failed" Error

**Cause**: Incorrect API key or username

**Solution:**
```python
# Verify settings_production.py has:
EMAIL_HOST_USER = 'apikey'  # Literally the string "apikey"
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY')

# Verify .env file has correct API key:
SENDGRID_API_KEY=SG.xxxxxx...
```

#### Issue: "Sender email not verified"

**Cause**: From email doesn't match verified sender

**Solution:**
1. Check `DEFAULT_FROM_EMAIL` matches verified sender exactly
2. Verify sender in SendGrid: Settings → Sender Authentication
3. Case-sensitive: `noreply@example.com` ≠ `NoReply@example.com`

#### Issue: Emails going to spam

**Solutions:**
1. Use Domain Authentication instead of Single Sender (requires DNS access)
2. Warm up your sender reputation (send gradually increasing volumes)
3. Ensure email content isn't spammy (avoid excessive links, caps, etc.)
4. Add unsubscribe link (required for bulk emails, not needed for transactional)

#### Issue: "Daily sending limit exceeded"

**Cause**: Sent more than 100 emails today

**Solutions:**
1. Wait until tomorrow (limit resets at midnight UTC)
2. Upgrade to paid plan if you need higher limits
3. Review why so many emails were sent (possible abuse/loop?)

#### Issue: SSL/TLS Connection Error

**Cause**: Firewall blocking port 587 or TLS disabled

**Solution:**
```python
# Verify in settings:
EMAIL_PORT = 587  # Not 465 or 25
EMAIL_USE_TLS = True  # Must be True for port 587
```

### Testing in Django Shell

To test email without going through the full password reset flow:

```bash
# On PythonAnywhere Bash console
workon meeting_scheduler
cd ~/CS3300_Metting_Calendar/meeting_scheduler
python manage.py shell
```

```python
from django.core.mail import send_mail

# Test basic email
send_mail(
    'Test Subject',
    'Test message body',
    'noreply@yourdomain.com',  # From (must match verified sender)
    ['your-email@gmail.com'],  # To
    fail_silently=False,
)

# Test password reset email (Django's built-in)
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

user = User.objects.get(username='testuser')
token = default_token_generator.make_token(user)
uid = urlsafe_base64_encode(force_bytes(user.pk))
print(f"Reset URL: /password-reset-confirm/{uid}/{token}/")
```

---

## Part 9: Scaling and Upgrading

### When to Upgrade

You should upgrade from the free tier if:
- ❌ Sending more than 100 emails/day
- ❌ Need better deliverability (domain authentication)
- ❌ Want advanced features (email templates, A/B testing, etc.)

### SendGrid Pricing Plans

**Free Forever:**
- 100 emails/day
- Basic email analytics
- Single sender verification
- Perfect for this project

**Essentials ($15/month):**
- 40,000 emails/month
- Email API
- Domain authentication
- 24/7 support

**Pro ($60/month):**
- 100,000 emails/month
- Advanced analytics
- Dedicated IP
- Team access

**For this project, the free tier is sufficient.**

### Usage Monitoring

Check current usage:
1. SendGrid dashboard → **Stats** → **Overview**
2. View emails sent today/this month
3. Set up alerts for approaching limits:
   - Dashboard → **Settings** → **Alerts**

---

## Security Best Practices

### ✅ DO:
- Store API keys in environment variables (`.env` file)
- Use `.gitignore` to exclude `.env` from version control
- Use TLS encryption (`EMAIL_USE_TLS = True`)
- Set restrictive file permissions on `.env` (`chmod 600`)
- Rotate API keys periodically (every 6-12 months)
- Monitor SendGrid activity for suspicious sends

### ❌ DON'T:
- Hardcode API keys in settings files
- Commit `.env` files to Git
- Share API keys via email/chat
- Use same API key for dev and production
- Give API keys more permissions than needed

### API Key Rotation

To rotate your API key periodically:

1. Create new API key in SendGrid (Settings → API Keys)
2. Update `.env` file with new key
3. Reload web app
4. Test email sending
5. Delete old API key in SendGrid

---

## Comparison: SendGrid vs. Gmail

| Feature | SendGrid Free | Gmail (App Password) |
|---------|---------------|----------------------|
| **Cost** | Free (100/day) | Free (500/day) |
| **Setup Complexity** | ⭐⭐ Medium | ⭐⭐⭐ Easy |
| **Professional** | ✅ Yes | ⚠️ Uses your Gmail |
| **Deliverability** | ✅ Excellent | ⚠️ Good |
| **Sender Email** | Any verified email | Must be Gmail address |
| **Analytics** | ✅ Yes | ❌ No |
| **API Key Auth** | ✅ Yes | ❌ Password-based |
| **Scalability** | ✅ Easy to upgrade | ⚠️ Limited to 500/day |
| **2FA Required** | ❌ No | ✅ Yes |

**Recommendation**: SendGrid for production, Gmail for quick testing.

---

## Quick Reference

### SendGrid SMTP Settings

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'
```

### Environment Variables (.env file)

```bash
SENDGRID_API_KEY=SG.your-api-key-here
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
DJANGO_SECRET_KEY=your-secret-key-here
```

### Test Email Command

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])
```

### Check SendGrid Activity

Dashboard → Activity → View all sent emails

---

## Support and Resources

**SendGrid Documentation:**
- Getting Started: https://docs.sendgrid.com/for-developers/sending-email/getting-started-smtp
- Django Integration: https://docs.sendgrid.com/for-developers/sending-email/django
- Troubleshooting: https://docs.sendgrid.com/for-developers/sending-email/troubleshooting

**SendGrid Support:**
- Free tier: Email support (24-48 hour response)
- Paid tiers: 24/7 support

**Django Email Documentation:**
- https://docs.djangoproject.com/en/5.1/topics/email/

**Project Documentation:**
- `DEPLOYMENT_PYTHONANYWHERE.md` - Full deployment guide
- `CLAUDE.md` - Development guide
- `SECURITY_GUIDE.md` - Security best practices

---

## Checklist: SendGrid Setup Complete

Use this checklist to verify your setup:

- ✅ SendGrid account created and verified
- ✅ Sender email verified (Single Sender Verification)
- ✅ API key created and saved securely
- ✅ `settings_production.py` configured with SendGrid settings
- ✅ `.env` file created with `SENDGRID_API_KEY`
- ✅ `python-decouple` installed
- ✅ `.env` added to `.gitignore`
- ✅ Test email sent successfully (local)
- ✅ Deployed to PythonAnywhere
- ✅ `.env` file created on PythonAnywhere
- ✅ Web app reloaded
- ✅ Password reset email tested (production)
- ✅ Email received successfully
- ✅ SendGrid activity dashboard shows sent email

**All checked? You're ready to send emails! 🎉**

---

**Last Updated**: 2025-11-03
**SendGrid Free Tier**: 100 emails/day
**Django Version**: 5.1.13
**Python Version**: 3.13
