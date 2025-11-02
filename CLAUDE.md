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
│   │   ├── settings.py         # Django settings (uses Django 5.1.6)
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

**Expected Result:** All 141 tests (93 unit + 16 fuzz + 32 other) must pass

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

✅ Pylint score: 9.0+ (or all issues fixed)
✅ Unit tests: 93/93 passing
✅ Fuzz tests: 16/16 passing
✅ Total tests: 141/141 passing
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
- Debug/Integration tests: 32 additional tests
- Total test cases: 141 tests + 350 fuzz-generated cases
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

### Security Best Practices

1. **Run security scans before committing code**
2. **Never commit SECRET_KEY or sensitive credentials**
3. **Keep Django and dependencies updated**
4. **Review Bandit/Semgrep findings and address issues**
5. **Use HTTPS in production environments**
6. **Regularly audit dependencies with Safety and pip-audit**

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
- **Current (Windows Development):** `EMAIL_BACKEND = 'calendar_app.email_backend.UnsecureEmailBackend'`
  - Gmail SMTP (smtp.gmail.com:465) with SSL bypass for Windows certificate issues
  - Real email sending via manchesterjm@gmail.com
- **Alternative (Console):** `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`
  - Emails printed to terminal (no real sending)
- **Production:** Use standard SMTP backend with environment variables for credentials

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

## Code Attribution

Comments in the codebase indicate:
- Django templates and standard files were adapted from course material (CS 2080)
- ChatGPT was used for troubleshooting code syntax
- Most customization focused on form handling and database operations
