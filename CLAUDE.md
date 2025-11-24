# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django-based meeting scheduler application (CS3300 course project) that manages user unavailability and calculates free time slots for scheduling meetings.

## Project Structure

```
CS3300_project/
├── meeting_scheduler/           # Django project root
│   ├── manage.py               # Django management script
│   ├── db.sqlite3              # SQLite database
│   ├── meeting_scheduler/      # Project configuration
│   │   ├── settings.py         # Django settings (uses Django 5.1.13)
│   │   ├── urls.py             # Root URL configuration
│   │   ├── wsgi.py             # WSGI application entry point
│   │   └── asgi.py             # ASGI application entry point
│   └── calendar_app/           # Main application
│       ├── models.py           # Unavailability model (date, start_time, end_time)
│       ├── views.py            # calendar_view handles all form submissions
│       ├── forms.py            # UnavailabilityForm and DeleteSelectedForm
│       ├── urls.py             # App URL routing
│       └── templates/calendar_app/
│           └── calendar.html   # Single-page UI with embedded CSS
└── forms.py                    # Duplicate/older forms.py in root (outdated)
```

## Initial Setup

### Documentation review
review all documents *.md prior to proceeding
ensure that guidance in these documents are adhered to prior to proceeding

### Prerequisites
Install Python 3, pip, and virtual environment tools:
```bash
sudo apt install python3 python3-pip python3-venv -y  # Ubuntu/Debian
```

### Virtual Environment Setup
Create and activate a virtual environment in the `meeting_scheduler/` directory:
```bash
cd meeting_scheduler
python3 -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows
```

### Install Django
```bash
pip install django
```

Or if a `requirements.txt` exists:
```bash
pip install -r requirements.txt
```

### Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

## Development Commands

All commands must be run from the `meeting_scheduler/` directory with the virtual environment activated.

### Running the Development Server

**Local access only:**
```bash
python manage.py runserver
```

**Network access (e.g., VM or remote access):**
```bash
python manage.py runserver 0.0.0.0:8000
```
Access at `http://<your-ip>:8000/`

**Background execution:**
```bash
nohup python manage.py runserver 0.0.0.0:8000 &
```
Logs written to `nohup.out`. Stop with `kill <PID>`.

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Create Superuser (Admin Access)
```bash
python manage.py createsuperuser
```

### Access Admin Interface
Navigate to `http://localhost:8000/admin/` after starting the server.

### Django Shell (Interactive Python with Django Context)
```bash
python manage.py shell
```

### Testing

## Testing Workflow

**IMPORTANT: All tests (pylint, unit, fuzz, and mutation) MUST be run every time code is updated.**

### Required Testing Process

- If a test server is being run, kill that process before proceeding with any testing to free up resources
- Display in the running log what step in the test workflow we are on for clarity

When updating code, follow this mandatory workflow:

#### Step 1: Run Pylint
```bash
cd meeting_scheduler
pylint calendar_app/*.py --disable=C0114,C0115,C0116,R0903,R0914,R0912,R0915,E1101 --max-line-length=120
```

**Note:** Disabled warnings:
- `C0114,C0115,C0116`: Missing docstrings (covered by code comments)
- `R0903`: Too few public methods (Django models/forms pattern)
- `R0914,R0912,R0915`: Too many locals/branches/statements (single-view architecture)
- `E1101`: Django ORM 'objects' member detection

**Action Required:**
- Never disable a pylint test because it makes more jobs to fix
- Fix ALL pylint findings before proceeding to tests
- All pylint actions will be handled, they will never be skipped for any reason
- Ensure code quality standards are met
- Re-run pylint after fixes to verify all issues resolved

#### Step 2: Run Unit Tests
```bash
python manage.py test calendar_app.tests --verbosity=2
```

**Action Required:**
- If ANY test fails, fix the error immediately
- Re-run tests after each fix
- Continue until ALL 27 tests pass

#### Step 3: Run Fuzz Tests
```bash
python manage.py test calendar_app.test_fuzz --verbosity=2
```

**Action Required:**
- If ANY test fails, fix the error immediately
- Re-run tests after each fix
- Continue until ALL 9 fuzz tests pass

#### Step 4: Run All Tests Together
```bash
python manage.py test calendar_app --verbosity=1
```

**Expected Result:** All 159 tests (93 unit + 16 fuzz + 50 other) must pass

#### Step 5: Run Mutation Tests
```bash
python run_mutation_test.py
```

**Action Required:**
- If ANY mutation survives, add tests to kill it
- Re-run mutation tests after adding new tests
- Continue until mutation score is 100%

#### Step 6: Verify Code Coverage
```bash
coverage run --source=calendar_app manage.py test calendar_app.tests
coverage report
```

**Expected Result:**
- Critical modules (models.py, forms.py, views.py) must maintain 93%+ coverage
- Overall coverage should be 80%+

#### Step 7: Run Security Scans
```bash
python run_security_scans.py
```

**Action Required:**
- Fix ALL security vulnerabilities before committing code
- Review and address all Bandit findings
- Update dependencies if Safety/pip-audit reports vulnerabilities
- Address Semgrep security pattern warnings
- Re-run security scans after fixes to verify all issues resolved

**Expected Result:**
- Bandit: 0 security issues
- Safety: 0 known vulnerabilities in dependencies
- pip-audit: 0 known vulnerabilities
- Semgrep: 0 security findings

### Quick Test Commands

**🚀 RECOMMENDED: Run automated test suite (all steps in order):**
```bash
python run_all_tests.py
```
This script automatically runs all 7 steps in order and stops at the first failure.

**Run all tests in one command:**
```bash
python manage.py test calendar_app && python run_mutation_test.py
```

**Full quality check (Pylint + All Tests + Coverage + Security):**
```bash
pylint calendar_app/*.py --disable=C0114,C0115,C0116,R0903,R0914,R0912,R0915,E1101 --max-line-length=120 && \
coverage run --source=calendar_app manage.py test calendar_app && \
coverage report && \
python run_mutation_test.py && \
python run_security_scans.py
```

**Generate HTML coverage report:**
```bash
coverage html  # Report in htmlcov/index.html
```

### Testing Standards

**All code changes MUST meet these criteria before being considered complete:**

✅ Pylint score: 10.00/10 (perfect score)
✅ Unit tests: 93/93 passing
✅ Fuzz tests: 16/16 passing
✅ Total tests: 159/159 passing
✅ Mutation score: 100%
✅ Code coverage: 93%+ on critical modules
✅ Security scans: 0 vulnerabilities (Bandit, Safety, pip-audit, Semgrep)
✅ No test failures or errors

**If any test fails:**
1. DO NOT proceed to next test type
2. Fix the error immediately
3. Re-run the failed test
4. Repeat until test passes
5. Then continue to next test type

### Current Test Statistics
- Unit tests: 93 tests covering models, forms, views, groups, and authentication
- Fuzz tests: 16 tests with ~350 generated test cases
- Debug/Integration tests: 50 additional tests (includes utils tests)
- Total test cases: 159 tests + 350 fuzz-generated cases
- Code coverage: 93%+ on critical modules (models, forms, views), 74% overall
- Mutation score: 100% (8/8 mutations killed)
- Test execution time: ~2 seconds

### New Feature Testing Policy

**MANDATORY REQUIREMENT: Every new feature added to this project MUST include comprehensive tests.**

When implementing ANY new feature, the following testing workflow is REQUIRED:

1. **Design tests before or during implementation**
   - Unit tests for all new models, forms, and views
   - Fuzz tests for any user input or data processing
   - Edge case tests for boundary conditions
   - Integration tests for multi-component features

2. **Run ALL existing tests to ensure no regressions**
   - All unit tests must pass
   - All fuzz tests must pass
   - Pylint score must remain 10.0/10
   - Mutation score must remain 100%

3. **Add feature-specific tests**
   - Write unit tests that cover all code paths in the new feature
   - Add fuzz tests if the feature handles user input
   - Update mutation tests to cover new mutations
   - Ensure code coverage remains at 93%+ for critical modules

4. **Iterate until all tests pass**
   - Fix any test failures immediately
   - Re-run tests after each fix
   - Continue until 100% pass rate achieved

5. **Verify code quality standards**
   - Run Pylint and fix all issues
   - Maintain 10.0/10 score (or address all findings)
   - Follow PEP 8 standards
   - Add comprehensive docstrings

6. **Run security scans**
   - Execute all security scanners (Bandit, Safety, pip-audit, Semgrep)
   - Fix all security vulnerabilities immediately
   - Update dependencies if vulnerabilities found
   - Ensure 0 security findings before proceeding

7. **Complete testing checklist**
   - ✅ Pylint: 10.0/10
   - ✅ Unit tests: All passing
   - ✅ Fuzz tests: All passing
   - ✅ Mutation tests: 100% score
   - ✅ Code coverage: 93%+ on critical modules
   - ✅ Security scans: 0 vulnerabilities
   - ✅ No test failures or errors

**NO FEATURE IS CONSIDERED COMPLETE UNTIL ALL TESTS AND SECURITY SCANS PASS.**

This policy ensures:
- High code quality and reliability
- No regressions introduced by new features
- Comprehensive test coverage maintained
- Consistent code standards across the project
- Early detection of bugs and security issues
- Zero-vulnerability codebase maintained

## Security Practices

### Security Scanning Tools

The project includes comprehensive security scanning tools configured for Django:

**Install security tools (development):**
```bash
pip install -r requirements-dev.txt
```

**Run all security scans:**
```bash
python run_security_scans.py
```

This automated script runs:
1. **Bandit** - Python security linter
2. **Safety** - Dependency vulnerability scanner
3. **pip-audit** - PyPI package vulnerability checker
4. **Semgrep** - Security pattern scanner for Django

**Run scans individually:**
```bash
# Static security analysis
bandit -r calendar_app/ --configfile .bandit -f txt

# Dependency vulnerability checks
safety scan
pip-audit -r requirements.txt

# Django-specific security patterns
semgrep --config=.semgrep.yml calendar_app/
```

### Security Configuration

**Bandit Configuration (`.bandit`):**
- Excludes test directories and migrations
- Skips B101 (assert usage - acceptable in tests)
- Skips B601 (shell=True - reviewed manually)

**Semgrep Rules (`.semgrep.yml`):**
- DEBUG=True detection in production
- Hardcoded SECRET_KEY detection
- SQL injection pattern matching
- XSS vulnerability detection (mark_safe usage)
- CSRF exemption warnings

### Production Security Settings

When deploying to production, update `meeting_scheduler/settings.py`:

1. **Set DEBUG to False:**
   ```python
   DEBUG = False
   ```

2. **Configure ALLOWED_HOSTS:**
   ```python
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   ```

3. **Use Environment Variable for SECRET_KEY:**
   ```python
   import os
   SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
   ```

4. **Enable HTTPS Security (uncomment in settings.py):**
   ```python
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   SECURE_HSTS_SECONDS = 31536000
   ```

### Security Features Enabled

The following security features are already configured:

- **Clickjacking Protection:** `X_FRAME_OPTIONS = 'DENY'`
- **MIME Type Sniffing Prevention:** `SECURE_CONTENT_TYPE_NOSNIFF = True`
- **XSS Protection:** `SECURE_BROWSER_XSS_FILTER = True`
- **Session Security:** HttpOnly cookies, Strict SameSite, 1-hour timeout
- **CSRF Protection:** HttpOnly tokens, Strict SameSite
- **Security Logging:** Configured to log security events to `logs/security.log`

### Dependencies

**Current versions (security-patched):**
- Django 5.1.13 (latest security release)
- All dependencies scanned for known vulnerabilities
- Regular updates required to maintain security

### CI/CD Security Automation

**GitHub Actions Workflows:**

The project includes automated security scanning in CI/CD:

1. **Security Workflow** (`.github/workflows/security.yml`)
   - Runs on all pushes and pull requests
   - Executes all 4 security scanners (Bandit, Safety, pip-audit, Semgrep)
   - Posts results as PR comments with detailed findings
   - Uploads scan results as artifacts
   - Non-blocking: reports issues but doesn't fail builds

2. **Dependabot** (`.github/dependabot.yml`)
   - Automatically monitors Python dependencies for security updates
   - Creates PRs for vulnerable or outdated packages
   - Groups dependencies (production vs development)
   - Weekly scans every Monday at 9:00 AM
   - Also monitors GitHub Actions workflow dependencies

**Workflow Triggers:**
- Runs automatically on every push to any branch
- Runs on all pull requests
- Results posted as sticky comments on PRs
- Scan artifacts available for download

**Managing Security Alerts:**
- Review Dependabot PRs weekly for security updates
- Address semgrep findings before merging
- Fix pip-audit vulnerabilities immediately
- Review Bandit warnings for false positives

### Security Best Practices

1. **Run security scans before committing code**
2. **Never commit SECRET_KEY or sensitive credentials**
3. **Keep Django and dependencies updated**
4. **Review Bandit/Semgrep findings and address issues**
5. **Use HTTPS in production environments**
6. **Regularly audit dependencies with Safety and pip-audit**
7. **Review and merge Dependabot security PRs promptly**
8. **Check CI/CD security workflow results on all PRs**

## Architecture Notes

### Calendar Architecture

**Personal Calendar** (`calendar_app/views.py` - `calendar_view`):
- Users manage their personal schedules
- Handles multiple POST actions via button names:
  - `submit_unavailability`: Adds new unavailability records
  - `show_free_times`: Calculates free 30-minute slots (8:00-20:00) based on user's unavailability
  - `show_last_five`: Displays the 5 most recent user entries
  - `delete_selected`: Deletes selected user entries

**Group Calendar** (`calendar_app/group_views.py` - `group_calendar_view`):
- Read-only view that aggregates ALL group members' personal calendars
- Shows common free times when everyone is available
- No manual entry management - automatically calculated
- Users manage schedules via personal calendar, group view shows aggregation

### Form Validation Strategy
The `UnavailabilityForm` uses conditional validation based on `submit_type`:
- Only validates non-default values when `submit_type='submit_unavailability'`
- Skips default-value checks for `show_free_times` action
- This prevents validation errors when users want to view free times without changing defaults

### Time Slot Calculation
Free time slots are calculated in 30-minute increments:
1. Generate all possible slots from 8:00 to 20:00 (30-minute intervals)
2. Mark slots as taken based on unavailability records
3. Return remaining slots as available times

### Database
- Uses SQLite (`db.sqlite3`)
- Models: `Unavailability` (with user ForeignKey), Django's built-in User model
- User authentication system with data isolation (users only see their own data)
- Default admin account available via `python manage.py create_default_admin`

### Authentication & Password Reset
- **User Authentication:** Registration, login, logout, account management
- **Password Reset:** Full workflow implemented with email support
- **Email Backend:** Console backend (development) - emails printed to terminal
- **Data Isolation:** Each user sees only their own unavailability entries
- **Admin Access:** Staff users can access Django admin panel via navbar
- **Mobile Responsive:** All auth pages work on phones and tablets

**Testing Password Reset:**
See `PASSWORD_RESET_GUIDE.md` for step-by-step testing instructions.

**Email Configuration (settings.py):**
- **Current (Development - Default):** `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`
  - Emails printed to terminal/logs (no real email sending)
  - No SMTP credentials required - secure for testing
  - Password reset links visible in console output
  - Recommended for development and testing
- **Optional (local_settings.py):** Real SMTP email sending
  - Uncomment SMTP configuration in `meeting_scheduler/local_settings.py`
  - Configure with environment variables (never hardcode credentials!)
  - Use for testing actual email delivery
- **Production:** Use standard SMTP backend with environment variables for credentials
  - Set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` environment variables
  - Never commit credentials to version control

**Password Reset URLs:**
- Request reset: `/password-reset/`
- Email sent confirmation: `/password-reset/done/`
- Set new password: `/password-reset-confirm/<uidb64>/<token>/`
- Success page: `/password-reset-complete/`

## Important Implementation Details

### Form Date/Time Defaults
- Date field defaults to current date (`datetime.date.today()`)
- Time fields default to `00:00` (midnight)
- Validation ensures users change defaults before submission to prevent database corruption

### Debug Output
The codebase includes `print()` statements for debugging form errors. These are intentionally left in for future developers to troubleshoot issues.

### Template Design
`calendar.html` includes:
- Embedded CSS with responsive design (`@media` queries for mobile)
- Django template tags for form rendering and error handling
- Success messages displayed via Django messages framework

## Configuration

### Settings (`meeting_scheduler/settings.py`)
- **Django Version**: 5.1.13 (security-patched)
- **Database**: SQLite3 at `BASE_DIR / 'db.sqlite3'`
- **Debug Mode**: `DEBUG = True` (development only - **MUST be False in production**)
- **Allowed Hosts**: Currently `['*']` (accepts all hosts). For production or VM deployment, update to specific IP addresses:
  ```python
  ALLOWED_HOSTS = ['128.198.51.79', 'localhost']  # Example
  ```
- **Secret Key**: Currently uses insecure default key (**MUST use environment variable in production**)
- **Time Zone**: UTC
- **Installed Apps**: Only `calendar_app` beyond Django defaults
- **Auto-reload**: With `DEBUG=True`, Django automatically reloads when files are modified
- **Security Settings**: Production-ready security headers and session configuration included (see Security Practices section)

## AI Code Review Fixes (November 2025)

### Overview
After receiving a comprehensive code review from ChatGPT AI, 8 of 14 identified issues have been addressed and merged into the `feature/auto-password-generation` branch.

### Completed Fixes (8/14)

**Critical Priority (3/3 - 100% Complete):**
1. **Security: Password Generation GET → POST** - Fixed vulnerability where generated passwords could leak through server logs. Changed all password generation endpoints from GET to POST with proper CSRF protection.
2. **Django Best Practice: Removed null=True from CharField** - Eliminated data inconsistency by removing `null=True` from `description` fields in both Unavailability and GroupUnavailability models. Created data migration to convert existing NULL values to empty strings.
3. **Error Handling: Specific Exceptions** - Replaced broad `except Exception` with specific `except (smtplib.SMTPException, OSError)` in email backend for better debugging.

**High Priority (4/4 - 100% Complete):**
4. **Code Duplication: BaseDescriptionForm** - Created mixin base class to eliminate 20 lines of duplicate `clean_description()` validation code across UnavailabilityForm and GroupUnavailabilityForm.
5. **Date Parsing Error Handling** - Enhanced error handling with explicit POST data validation and improved error messages (changed from generic "invalid date" to format-specific "use YYYY-MM-DD").
6. **POST Data Validation** - Added explicit checks for missing/empty date fields before parsing to prevent crashes from malformed requests.
7. **Timezone Handling** - Updated `calculate_free_time_slots()` utility to use timezone-aware datetime objects with `django.utils.timezone.make_aware()` for correct multi-timezone calculations.

**Medium Priority (1/4 - 25% Complete):**
9. **User Feedback for Empty free_times** - Added positive UX feedback message when all time slots are free (no unavailability entries), replacing blank sections with celebratory "All slots free!" message.

### Remaining Issues (6/14)

**Medium Priority (3 remaining):**
- **#8**: Extract JavaScript to external files (improves maintainability, enables browser caching)
- **#10**: Document or refactor admin User customization pattern (potential conflicts with other apps)
- **#11**: Add JavaScript testing framework (Jest setup + test files)

**Low Priority (3 remaining):**
- **#12**: Document Pylint disables in STYLE_GUIDE.md (justified in code, needs formal documentation)
- **#13**: UnsecureEmailBackend (✅ already properly handled with runtime checks)
- **#14**: Split tests.py into multiple test modules (~1350 lines → test_models.py, test_forms.py, etc.)

### Testing Results After Fixes
- ✅ All 159 tests passing (93 unit + 16 fuzz + 50 other)
- ✅ Pylint score: 10.00/10 (no warnings or errors)
- ✅ Code coverage: 93%+ on critical modules (models, forms, views)
- ✅ Mutation score: 100% (8/8 mutations killed)
- ✅ Security scans: 0 vulnerabilities (Bandit, pip-audit, Semgrep)

### Git Commits
- `372b5ab` - fix: Address critical AI code review findings (#1-3)
- `037e09b` - fix: Address high-priority AI code review findings (#4-7)
- `e08dc4f` - fix: Add user feedback for empty free_times in calendar views (#9)

### Documentation References
- **AI_CODE_REVIEW_FIXES.md**: Detailed tracking of all 14 issues with status, required changes, and progress
- **GITHUB_ISSUES_TO_CREATE.md**: Templates for creating GitHub issues for remaining 6 items
- **Branch**: feature/auto-password-generation

---

## Troubleshooting

This section covers common issues and their solutions for the Meeting Scheduler application.

### Server and Network Issues

#### Issue: "Address already in use" when starting server
**Symptoms**: `Error: That port is already in use.` or similar message

**Solutions**:
```bash
# Option 1: Find and kill the process using port 8000 (Linux/Mac)
lsof -ti:8000 | xargs kill -9

# Option 2: Find and kill the process (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Option 3: Use a different port
python manage.py runserver 8080
```

#### Issue: Cannot access server from another machine/VM
**Symptoms**: Server starts but cannot connect from network

**Solutions**:
1. **Check if server is bound to 0.0.0.0**:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

2. **Update ALLOWED_HOSTS in settings.py**:
   ```python
   ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'your-vm-ip', '*']  # For dev only
   ```

3. **Check firewall settings**:
   ```bash
   # Linux: Allow port 8000
   sudo ufw allow 8000/tcp

   # Windows: Add inbound rule in Windows Defender Firewall
   # Go to: Windows Defender Firewall → Advanced Settings → Inbound Rules → New Rule
   ```

4. **Verify IP address**:
   ```bash
   # Linux/Mac
   ifconfig | grep inet

   # Windows
   ipconfig
   ```

#### Issue: Static files not loading (CSS/JS missing)
**Symptoms**: Pages render without styling, JavaScript not working

**Solutions**:
1. **Collect static files** (production):
   ```bash
   python manage.py collectstatic
   ```

2. **Check DEBUG mode** (development):
   ```python
   # In settings.py
   DEBUG = True  # Serves static files automatically in dev mode
   ```

3. **Verify static file configuration**:
   ```python
   # In settings.py
   STATIC_URL = '/static/'
   STATICFILES_DIRS = [BASE_DIR / 'static']
   ```

### Database Issues

#### Issue: "no such table" errors
**Symptoms**: `django.db.utils.OperationalError: no such table: calendar_app_unavailability`

**Solutions**:
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# If migrations exist but aren't applied
python manage.py migrate --run-syncdb

# Check migration status
python manage.py showmigrations
```

#### Issue: Database is locked
**Symptoms**: `database is locked` error during operations

**Solutions**:
```bash
# Option 1: Restart the server (SQLite doesn't support concurrent writes well)
# Option 2: Check for background processes accessing the database
# Option 3: Delete db.sqlite3 and recreate (DEVELOPMENT ONLY - loses all data!)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

#### Issue: Migration conflicts
**Symptoms**: `Conflicting migrations detected` or migration order issues

**Solutions**:
```bash
# Option 1: Reset migrations (DEVELOPMENT ONLY)
# Delete calendar_app/migrations/*.py (except __init__.py)
# Delete db.sqlite3
python manage.py makemigrations calendar_app
python manage.py migrate

# Option 2: Merge migrations
python manage.py makemigrations --merge
```

### Testing Issues

#### Issue: Tests fail with "test database cannot be created"
**Symptoms**: Permission errors creating test database

**Solutions**:
```bash
# Ensure you have write permissions in the project directory
chmod +w meeting_scheduler/

# On Windows, run as administrator if needed
```

#### Issue: Import errors when running tests
**Symptoms**: `ModuleNotFoundError` or `ImportError` during test execution

**Solutions**:
```bash
# Ensure virtual environment is activated
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows

# Reinstall requirements
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Issue: Mutation tests fail unexpectedly
**Symptoms**: Mutation score drops below 100%

**Solutions**:
```bash
# Run mutation tests with verbose output
python run_mutation_test.py

# Check which mutations survived and add tests to kill them
# Review the mutation test output for details
```

### Authentication and Password Issues

#### Issue: Cannot login with created user
**Symptoms**: "Invalid credentials" even with correct password

**Solutions**:
```python
# In Django shell, reset the password
python manage.py shell

from django.contrib.auth.models import User
user = User.objects.get(username='your_username')
user.set_password('new_password')
user.save()
exit()
```

#### Issue: Password reset emails not working
**Symptoms**: Password reset doesn't send emails

**Solutions**:
1. **Check email backend** (development uses console):
   ```python
   # In settings.py or local_settings.py
   EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
   # Emails will print to console/terminal instead
   ```

2. **For real email** (production):
   ```python
   # Use environment variables, NEVER hardcode credentials
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'smtp.gmail.com'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
   EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
   ```

3. **Check spam folder** if using real email

### Dependency Issues

#### Issue: Module import errors after pip install
**Symptoms**: `ModuleNotFoundError` even after installing packages

**Solutions**:
```bash
# Verify virtual environment is activated
which python  # Linux/Mac - should show env/bin/python
where python  # Windows - should show env\Scripts\python.exe

# Reinstall in correct environment
pip uninstall <package>
pip install <package>

# Check installed packages
pip list

# Upgrade pip itself
python -m pip install --upgrade pip
```

#### Issue: Version conflicts
**Symptoms**: `ERROR: pip's dependency resolver does not currently take into account all the packages...`

**Solutions**:
```bash
# Create fresh virtual environment
deactivate  # Exit current venv
rm -rf env  # Delete old venv
python3 -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Security Scan Issues

#### Issue: Bandit false positives
**Symptoms**: Security warnings for development-only code

**Solutions**:
- Check `.bandit` configuration file
- Development-only workarounds (like UnsecureEmailBackend) have runtime checks preventing production use
- Review SECURITY_GUIDE.md for justification of each disable

#### Issue: pip-audit reports vulnerabilities
**Symptoms**: Known vulnerabilities in dependencies

**Solutions**:
```bash
# Update specific package
pip install --upgrade <package>

# Update Django
pip install --upgrade django

# Check for security updates
pip list --outdated
```

### Production Deployment Issues

#### Issue: DEBUG=False causes 500 errors
**Symptoms**: Site works in development but not production

**Checklist**:
1. **Set ALLOWED_HOSTS**:
   ```python
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   ```

2. **Collect static files**:
   ```bash
   python manage.py collectstatic
   ```

3. **Use environment variables for secrets**:
   ```python
   SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
   ```

4. **Enable HTTPS security** (uncomment in settings.py):
   ```python
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

5. **Check error logs**:
   ```bash
   tail -f logs/django.log
   tail -f logs/security.log
   ```

### Common Error Messages

#### "CSRF verification failed"
**Solutions**:
- Ensure `{% csrf_token %}` is in all forms
- Check that cookies are enabled in browser
- Verify CSRF_COOKIE_HTTPONLY and CSRF_COOKIE_SAMESITE settings

#### "ImproperlyConfigured: The SECRET_KEY setting must not be empty"
**Solutions**:
```bash
# Generate new secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Set as environment variable
export DJANGO_SECRET_KEY='your-generated-key'  # Linux/Mac
set DJANGO_SECRET_KEY=your-generated-key  # Windows

# Or set in settings.py (development only)
SECRET_KEY = 'your-generated-key'
```

#### "DisallowedHost at /"
**Solutions**:
```python
# Add your hostname to ALLOWED_HOSTS in settings.py
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'your-hostname']
```

### Performance Issues

#### Issue: Slow page loads with many group members
**Symptoms**: Group calendar takes a long time to load

**Solutions**:
- N+1 query optimization already implemented with `.select_related('user')`
- Consider pagination for very large groups (100+ members)
- Add database indexes if needed:
  ```python
  class Meta:
      indexes = [
          models.Index(fields=['user', 'date']),
      ]
  ```

### Getting Help

If you encounter an issue not covered here:

1. **Check Django documentation**: https://docs.djangoproject.com/
2. **Review error logs**: `logs/django.log` and `logs/security.log`
3. **Enable DEBUG mode** (development only) for detailed error pages
4. **Check test output**: Run `python manage.py test calendar_app --verbosity=2`
5. **Review STYLE_GUIDE.md**: For coding standards and patterns
6. **Review SECURITY_GUIDE.md**: For security-related issues

---

## Production Deployment

### Deployment Platform

**Recommended Platform**: PythonAnywhere ($5/month Hacker Plan)

This project is configured for deployment on PythonAnywhere, which provides:
- Built-in SMTP support for email
- Easy Django deployment
- Automatic HTTPS
- SSH access for Git operations
- SQLite database (suitable for this application)

### Deployment Documentation

See **DEPLOYMENT_PYTHONANYWHERE.md** for complete step-by-step deployment instructions.

**Quick Start**:
1. Sign up for PythonAnywhere Hacker Plan ($5/month)
2. Clone repository via SSH
3. Create virtual environment and install dependencies
4. Configure WSGI file and production settings
5. Set up Gmail app password for email
6. Run migrations and collect static files
7. Test and go live

**Checklist**: See **DEPLOYMENT_CHECKLIST.md** for a quick reference deployment checklist.

### Custom Domain Setup

To use a custom domain (e.g., syncmeet.com):
1. Register domain and add to Cloudflare
2. Configure DNS: CNAME → `your-username.pythonanywhere.com`
3. Add custom domain in PythonAnywhere Web tab (+$1/month)
4. Update ALLOWED_HOSTS in production settings
5. SSL/TLS handled automatically by PythonAnywhere

### Production Configuration Files

- **settings_production.py** - Production Django settings
- **.env.example** - Template for environment variables
- **requirements.txt** - Python dependencies for production

### Post-Deployment

After deployment:
- Test all features (auth, calendar, groups, email)
- Monitor error logs at `~/logs/django_error.log`
- Set up database backup schedule
- Consider implementing meeting proposal feature

---

## Code Attribution

Comments in the codebase indicate:
- Django templates and standard files were adapted from course material (CS 2080)
- ChatGPT was used for troubleshooting code syntax and comprehensive code review (November 2025)
- Most customization focused on form handling and database operations
- Claude Code (Anthropic) used for implementing AI code review fixes
