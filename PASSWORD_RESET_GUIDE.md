# Password Reset Testing Guide

## Current Configuration ✅

**Email Backend:** Gmail SMTP (with Windows SSL bypass for development)
- Real email sending via Gmail SMTP (smtp.gmail.com:465)
- Uses custom UnsecureEmailBackend for Windows SSL certificate issues
- Emails sent to actual email addresses
- Password reset links work in real inboxes
- **Note**: Windows development only - production uses standard Django email backend

**Alternative Configuration Available:**
- Console backend available for testing without email (see section below)

## How to Test Password Reset

### Method 1: Test with Real Email (Gmail SMTP)

1. **Start the development server:**
   ```bash
   cd meeting_scheduler
   python manage.py runserver 0.0.0.0:8000
   ```

2. **Open your browser:**
   - Go to: `http://localhost:8000/login/`

3. **Click "Forgot your password?"**

4. **Enter a real email address** (your email or test email):
   - Enter: `your-email@gmail.com` (must be real)
   - Click "Send Reset Instructions"

5. **Check your email inbox:**
   - Email sent from: manchesterjm@gmail.com
   - Subject: "Password reset on 127.0.0.1:8000"
   - Look for a section like:
   ```
   From: manchesterjm@gmail.com
   To: your-email@gmail.com
   Subject: Password reset on 127.0.0.1:8000

   You're receiving this email because you requested a password reset...

   Please go to the following page and choose a new password:

   http://127.0.0.1:8000/password-reset-confirm/...

   Your username, in case you've forgotten: yourusername
   ```

6. **Click the password reset link** in your email

7. **Enter your new password** (twice)

8. **Click "Change My Password"**

9. **Login with your new password!**

### Method 2: Test with Default Admin

```bash
cd meeting_scheduler
python manage.py create_default_admin
python manage.py runserver 0.0.0.0:8000
```

Then follow steps 2-10 above, using `admin@meetingcalendar.local` as the email.

## For Class Demos

### Show the Feature Works:

1. **Open email on phone/another device** and browser on computer
2. **Point out to instructor:** "Using Gmail SMTP for real email delivery"
3. **Navigate through password reset flow** in browser
4. **Show the email in your inbox** when it arrives
5. **Click the link** from email and demonstrate it works
6. **Successfully reset password** and login

### Key Talking Points:

- ✅ "Using Django's built-in password reset system"
- ✅ "Gmail SMTP configured for real email delivery"
- ✅ "Custom SSL bypass backend for Windows development"
- ✅ "Email includes secure token that expires"
- ✅ "Full password reset workflow implemented"

## Email Configuration Details

**Current Setup (Windows Development):**
```python
# meeting_scheduler/settings.py
EMAIL_BACKEND = 'calendar_app.email_backend.UnsecureEmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'manchesterjm@gmail.com'
EMAIL_HOST_PASSWORD = 'ntuibnehkvahqvna'  # Gmail App Password
DEFAULT_FROM_EMAIL = 'manchesterjm@gmail.com'
```

**Why Custom Backend?**
- Windows has SSL certificate verification issues with Python
- Custom `UnsecureEmailBackend` bypasses SSL verification for development
- Production would use standard `django.core.mail.backends.smtp.EmailBackend`
- Security note: This is documented and acceptable for development only

## Real Email Output Example

```
From: manchesterjm@gmail.com
To: user@example.com
Subject: Password reset on 127.0.0.1:8000
Date: Sat, 02 Jan 2025 14:30:45 -0000

You're receiving this email because you requested a password reset for your user account at 127.0.0.1:8000.

Please go to the following page and choose a new password:

http://127.0.0.1:8000/password-reset-confirm/MQ/c5kj7h-e3f8a9b2c1d4e5f6a7b8c9d0e1f2a3b4/

Your username, in case you've forgotten: testuser

Thanks for using our site!

The 127.0.0.1:8000 team
```

## Alternative: Console Backend (No Email)

For testing without real email, switch to console backend:

**Change in `meeting_scheduler/settings.py`:**
```python
# Comment out Gmail SMTP:
# EMAIL_BACKEND = 'calendar_app.email_backend.UnsecureEmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# ...

# Enable console backend:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Then emails will print to terminal instead of sending.

## Production Email Configuration

For production deployment, use standard Django SMTP backend:

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')
```

**Use environment variables for security!**

## Troubleshooting

**Problem:** Email not arriving in inbox
- **Solution 1:** Check spam/junk folder
- **Solution 2:** Verify email address is correct
- **Solution 3:** Check terminal for SMTP errors
- **Solution 4:** Wait a few minutes (SMTP can be slow)

**Problem:** SMTP connection error
- **Solution:** Check internet connection and firewall settings

**Problem:** SSL certificate error (non-Windows)
- **Solution:** Use standard SMTP backend with `EMAIL_USE_TLS = True` and port 587

**Problem:** Password reset link doesn't work
- **Solution:** Make sure you clicked the entire link from email

**Problem:** Link says "invalid or expired"
- **Solution:** Links expire after 20 minutes. Request a new password reset.

**Problem:** Want to test multiple times
- **Solution:** Just request password reset again - you can do it unlimited times

**Problem:** Custom backend security warning
- **Solution:** This is expected - Windows development only. Production uses standard backend.

## Features Demonstrated

✅ User can request password reset via email
✅ System generates secure, time-limited token
✅ Email contains password reset link
✅ User can set new password
✅ Old password is invalidated
✅ User can login with new password
✅ Mobile-responsive templates
✅ Clear user instructions at each step

## URLs

- Password reset request: `/password-reset/`
- Email sent confirmation: `/password-reset/done/`
- Set new password: `/password-reset-confirm/<token>/`
- Success message: `/password-reset-complete/`

## Files Involved

- `calendar_app/urls.py` - URL routing
- `meeting_scheduler/settings.py` - Email configuration (Gmail SMTP)
- `calendar_app/email_backend.py` - Custom SSL bypass backend for Windows
- `calendar_app/templates/calendar_app/password_reset*.html` - Templates
- Django's built-in `auth.views` - Password reset logic

## Security Notes

**Custom Email Backend:**
- File: `calendar_app/email_backend.py`
- Purpose: Bypass SSL certificate verification on Windows
- Usage: Development only
- Bandit Warning: Expected (documented in code)
- Production: Use standard Django SMTP backend

**Gmail App Password:**
- Currently hardcoded in settings.py (development only)
- Production: Use environment variables
- Stored in: `EMAIL_HOST_PASSWORD` setting
- Security: Do not commit real passwords to version control

---

**Current Status:** ✅ Fully implemented with Gmail SMTP and ready to demo!
