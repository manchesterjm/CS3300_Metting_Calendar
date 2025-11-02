# Progressive Web App (PWA) Guide

This guide explains how the Meeting Scheduler has been configured as a Progressive Web App, allowing users to install it on their Android/iOS devices and use it like a native app.

## What is a PWA?

A Progressive Web App is a web application that uses modern web capabilities to deliver an app-like experience to users. It can be installed on mobile devices, work offline, send push notifications, and more.

## Features Implemented

### 1. Web App Manifest (`manifest.json`)
- **Location**: `calendar_app/static/calendar_app/manifest.json`
- **Purpose**: Defines app metadata (name, icons, colors, display mode)
- **Features**:
  - App name: "Meeting Scheduler"
  - Standalone display mode (full-screen like native app)
  - Theme color: #1abc9c (teal)
  - Background color: #2c3e50 (dark blue)
  - App shortcuts to Calendar and Groups pages
  - Icons in 8 different sizes (72px to 512px)

### 2. Service Worker (`service-worker.js`)
- **Location**: `calendar_app/static/calendar_app/service-worker.js`
- **Purpose**: Enables offline functionality and caching
- **Caching Strategies**:
  - **Cache-first** for static assets (CSS, JS, images)
  - **Network-first** for dynamic content (HTML pages, API calls)
  - Automatic cache versioning and cleanup
  - Maximum 50 cached dynamic pages

### 3. App Icons
- **Location**: `calendar_app/static/calendar_app/icons/`
- **Sizes**: 72x72, 96x96, 128x128, 144x144, 152x152, 192x192, 384x384, 512x512
- **Generation**: Run `python generate_pwa_icons.py` to regenerate icons
- **Design**: Gradient background (teal to dark blue) with "MS" text

### 4. PWA Meta Tags
- **Location**: Added to `base.html` template
- **Includes**:
  - Theme color for browser UI
  - Apple-specific meta tags for iOS support
  - Mobile web app capability tags
  - Apple Touch Icons for iOS home screen

## Installation Instructions

### For Users (Installing on Android)

1. **Open the app in Chrome or Edge**:
   - Navigate to your deployed app URL (must be HTTPS)
   - Example: `https://yourdomain.com/`

2. **Install the app**:
   - Chrome will show an "Install" banner at the bottom
   - Tap "Install" or use the menu → "Add to Home screen"
   - The app icon will appear on your home screen

3. **Using the installed app**:
   - Tap the icon to launch the app full-screen
   - Works offline (cached pages)
   - Looks and feels like a native app

### For Users (Installing on iOS)

1. **Open the app in Safari**:
   - Navigate to your deployed app URL
   - iOS requires Safari for PWA installation

2. **Add to Home Screen**:
   - Tap the Share button (box with arrow)
   - Scroll down and tap "Add to Home Screen"
   - Edit the name if desired, then tap "Add"

3. **Using the installed app**:
   - Tap the icon to launch the app
   - Limited offline support on iOS (basic caching only)

## Development Setup

### Prerequisites
- Python 3.8+
- Django 5.1.13+
- Pillow library (for icon generation)

### Generating Icons
```bash
# Install Pillow if not already installed
pip install Pillow

# Generate PWA icons
cd meeting_scheduler
python generate_pwa_icons.py
```

This creates 8 icon files in `calendar_app/static/calendar_app/icons/`.

### Testing PWA Locally

**IMPORTANT**: PWAs require HTTPS in production, but localhost works for testing.

1. **Run Django development server**:
   ```bash
   python manage.py runserver
   ```

2. **Test in Chrome**:
   - Open `http://localhost:8000/`
   - Open Chrome DevTools (F12)
   - Go to "Application" tab
   - Check "Manifest" section for manifest errors
   - Check "Service Workers" section for registration
   - Use "Lighthouse" tab to audit PWA compliance

3. **Test PWA features**:
   - Check "Offline" checkbox in DevTools → Network tab
   - Reload page to test offline functionality
   - Uncheck to go back online

### Testing on Android Device

1. **Deploy to a server with HTTPS**:
   - Use a service like Render, Heroku, or DigitalOcean
   - Ensure HTTPS is enabled (required for service workers)

2. **Access from Android Chrome**:
   - Open the deployed URL on your Android device
   - Install banner should appear automatically

3. **Manual installation** (if banner doesn't appear):
   - Chrome menu → "Install app" or "Add to Home screen"

## Production Deployment

### Requirements
- ✅ HTTPS enabled (required for service workers)
- ✅ Valid SSL certificate
- ✅ `collectstatic` run to serve static files
- ✅ Manifest and service worker accessible

### Django Settings for Production

```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Deployment Checklist

- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Enable HTTPS/SSL
- [ ] Run `python manage.py collectstatic`
- [ ] Test manifest at `/static/calendar_app/manifest.json`
- [ ] Test service worker registration
- [ ] Test installation on Android device
- [ ] Verify offline functionality works
- [ ] Check Lighthouse PWA score (should be 90+)

## PWA Features

### Currently Implemented
- ✅ Installable on Android/iOS
- ✅ Offline page caching
- ✅ App shortcuts (Calendar, Groups)
- ✅ Full-screen standalone mode
- ✅ Custom theme colors
- ✅ Multiple icon sizes
- ✅ Automatic service worker updates

### Future Enhancements (Optional)
- [ ] Push notifications for meeting reminders
- [ ] Background sync for offline form submissions
- [ ] Offline data editing with IndexedDB
- [ ] Share target API (share meetings to app)
- [ ] App badging API (notification counts)
- [ ] Periodic background sync

## Troubleshooting

### Service Worker Not Registering
- **Check**: Browser console for errors
- **Ensure**: Using HTTPS (or localhost for testing)
- **Verify**: Service worker file is accessible at correct path
- **Clear**: Browser cache and reload

### Install Banner Not Showing
- **Requirements**:
  - HTTPS enabled
  - Valid manifest.json
  - Service worker registered
  - At least 192x192 icon
  - User hasn't dismissed banner 3 times
- **Test**: Chrome DevTools → Application → Manifest

### Icons Not Displaying
- **Check**: Icon paths in manifest.json
- **Verify**: Icons exist in `static/calendar_app/icons/`
- **Run**: `python manage.py collectstatic` in production
- **Test**: Access icon URLs directly in browser

### Offline Mode Not Working
- **Check**: Service worker registration in DevTools
- **Verify**: Cache storage has entries
- **Test**: Go offline in DevTools and reload
- **Clear**: Service worker and cache, re-register

### iOS Issues
- **Note**: iOS has limited PWA support
- **Use**: Safari (not Chrome) for installation
- **Known Limitations**:
  - No push notifications
  - Limited background sync
  - Service worker restrictions

## Resources

- [MDN PWA Documentation](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Google PWA Checklist](https://web.dev/pwa-checklist/)
- [Web App Manifest Spec](https://w3c.github.io/manifest/)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Lighthouse PWA Audit](https://developers.google.com/web/tools/lighthouse)

## Testing Checklist

Before deploying, verify:

- [ ] Manifest loads without errors
- [ ] Service worker registers successfully
- [ ] All 8 icon sizes exist
- [ ] App installs on Android Chrome
- [ ] Offline mode caches pages
- [ ] Theme color displays correctly
- [ ] App shortcuts work
- [ ] Lighthouse PWA score is 90+
- [ ] HTTPS enabled in production

## Support

For issues or questions about PWA functionality:
1. Check browser console for errors
2. Use Chrome DevTools Application tab
3. Review this guide's troubleshooting section
4. Test with Lighthouse audit

---

**Generated with Claude Code** • PWA Implementation Guide v1.0
