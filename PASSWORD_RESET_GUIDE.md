# Password Reset Testing Guide

## Current Configuration ✅

**Email Backend:** Console (Development Mode)
- Emails are printed to the terminal/console
- No external SMTP server needed
- Perfect for local development and demos
- Already configured and working

## How to Test Password Reset

### Method 1: Test with Existing User

1. **Start the development server:**
   ```bash
   cd meeting_scheduler
   python manage.py runserver 0.0.0.0:8000
   ```

2. **Open your browser:**
   - Go to: `http://localhost:8000/login/`

3. **Click "Forgot your password?"**

4. **Enter any email address** (doesn't need to be real):
   - Enter: `test@example.com` (or any email)
   - Click "Send Reset Instructions"

5. **Check your terminal/console** where the server is running:
   - You'll see the password reset email printed
   - Look for a section like:
   ```
   Content-Type: text/plain; charset="utf-8"
   MIME-Version: 1.0
   Content-Transfer-Encoding: 7bit
   Subject: Password reset on localhost:8000
   From: noreply@meetingcalendar.local
   To: test@example.com

   You're receiving this email because you requested a password reset...

   Please go to the following page and choose a new password:

   http://localhost:8000/password-reset-confirm/...
   ```

6. **Copy the password reset link** from the terminal

7. **Paste the link in your browser**

8. **Enter your new password** (twice)

9. **Click "Change My Password"**

10. **Login with your new password!**

### Method 2: Test with Default Admin

```bash
cd meeting_scheduler
python manage.py create_default_admin
python manage.py runserver 0.0.0.0:8000
```

Then follow steps 2-10 above, using `admin@meetingcalendar.local` as the email.

## For Class Demos

### Show the Feature Works:

1. **Split your screen:** Terminal on one side, browser on the other
2. **Point out to instructor:** "Emails are displayed in console for development"
3. **Navigate through password reset flow** in browser
4. **Show the email in terminal** when it appears
5. **Copy the link** and demonstrate it works
6. **Successfully reset password** and login

### Key Talking Points:

- ✅ "Using Django's built-in password reset system"
- ✅ "Console backend for development - would use SMTP in production"
- ✅ "Email includes secure token that expires"
- ✅ "Full password reset workflow implemented"

## Console Email Output Example

```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Password reset on localhost:8000
From: noreply@meetingcalendar.local
To: admin@meetingcalendar.local
Date: Sat, 02 Nov 2024 10:30:45 -0000
Message-ID: <...>

You're receiving this email because you requested a password reset for your user account at localhost:8000.

Please go to the following page and choose a new password:

http://localhost:8000/password-reset-confirm/MQ/c5kj7h-e3f8a9b2c1d4e5f6a7b8c9d0e1f2a3b4/

Your username, in case you've forgotten: admin

Thanks for using our site!

The localhost:8000 team
```

## Switching to Production Email (Future)

If you need real email delivery later, uncomment these lines in `meeting_scheduler/settings.py`:

```python
# For Gmail SMTP (free):
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Get from Google Account
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

And comment out the console backend:
```python
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

## Troubleshooting

**Problem:** Don't see email in console
- **Solution:** Make sure you're looking at the terminal where `runserver` is running

**Problem:** Password reset link doesn't work
- **Solution:** Make sure you copied the entire link (it's long)

**Problem:** Link says "invalid or expired"
- **Solution:** Links expire after some time. Request a new password reset.

**Problem:** Want to test multiple times
- **Solution:** Just request password reset again - you can do it unlimited times

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
- `meeting_scheduler/settings.py` - Email configuration
- `calendar_app/templates/calendar_app/password_reset*.html` - Templates
- Django's built-in `auth.views` - Password reset logic

---

**Current Status:** ✅ Fully implemented and ready to demo!
