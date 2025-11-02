# Security & Bug Detection Guide

**Meeting Scheduler - Security Best Practices**

**Version**: 2.0
**Last Updated**: January 11, 2025
**Project**: CS3300 Meeting Scheduler Application

This document outlines security best practices, vulnerability scanning tools, and bug detection strategies for the Meeting Scheduler application. All team members must follow these guidelines to ensure application security and reliability.

---

## Table of Contents

1. [Security Principles](#security-principles)
2. [Current Security Implementation](#current-security-implementation)
3. [Security Scanning Tools](#security-scanning-tools)
4. [Common Vulnerabilities](#common-vulnerabilities)
5. [Input Validation](#input-validation)
6. [Authentication & Authorization](#authentication--authorization)
7. [Data Protection](#data-protection)
8. [Logging & Monitoring](#logging--monitoring)
9. [Dependencies & Supply Chain](#dependencies--supply-chain)
10. [Security Testing](#security-testing)
11. [Bug Detection Strategies](#bug-detection-strategies)
12. [Incident Response](#incident-response)
13. [Security Checklist](#security-checklist)

---

## Security Principles

### Core Security Values
1. **Defense in Depth**: Multiple layers of security
2. **Least Privilege**: Minimal necessary access only
3. **Fail Securely**: Errors should not expose sensitive data
4. **Security by Design**: Build security in from the start
5. **Never Trust User Input**: Validate everything
6. **Keep It Simple**: Complex code has more vulnerabilities

### Security Mindset
- **Assume Breach**: Plan for when (not if) security fails
- **Think Like an Attacker**: Consider abuse cases
- **Document Security Decisions**: Explain why you chose certain approaches
- **Stay Updated**: Security landscape constantly evolves

---

## Current Security Implementation

### Implemented Protections (January 2025)

#### Authentication Security
- **User Authentication**: Django's built-in authentication system
- **Password Requirements**: Minimum 8 characters, complexity validation
- **Secure Password Reset**: Token-based with 1-hour expiration
- **Session Management**: HttpOnly cookies, Strict SameSite, 1-hour timeout
- **Generic Error Messages**: Prevents user enumeration
- **Account Management**: Users can update profile and change password

#### Input Validation
- **Form Validation**: Django forms with field-level validation
- **Date/Time Validation**: Server-side validation of dates and time ranges
- **Length Limits**: Reasonable character limits on all text inputs
- **Email Validation**: Format checking before account creation
- **Empty Field Validation**: All required inputs checked

#### Network Security
- **HTTPS Only**: Required in production
- **X-Frame-Options**: DENY (clickjacking protection)
- **Content-Type-Nosniff**: Prevents MIME sniffing
- **XSS-Protection**: Browser XSS filter enabled

#### Data Protection
- **CSRF Protection**: Django's built-in CSRF tokens on all forms
- **SQL Injection Protection**: Django ORM parameterized queries
- **XSS Protection**: Django's automatic HTML escaping
- **Password Hashing**: PBKDF2 with strong key derivation
- **Environment Variable Usage**: No secrets in code

#### Testing
- **Security Test Suite**: Input validation, authentication, authorization tests
- **141 Tests Total**: 93 unit + 16 fuzz + 32 debug/integration
- **93%+ Code Coverage**: On critical modules (models, forms, views)
- **100% Mutation Score**: All mutations killed
- **CI/CD**: Automated testing on all pushes/PRs

**See CLAUDE.md** for detailed security feature documentation.

---

## Security Scanning Tools

### Recommended Tools for Django/Python

#### 1. Bandit - Python Security Linter
**Purpose**: Static analysis for common security issues in Python code

```bash
# Installation
pip install bandit

# Basic usage
bandit -r calendar_app/ meeting_scheduler/

# With configuration file
bandit -r calendar_app/ -c .bandit

# Generate HTML report
bandit -r calendar_app/ -f html -o bandit-report.html

# CI-friendly format
bandit -r calendar_app/ -f json -o bandit-report.json
```

**What it detects**:
- Hardcoded passwords or API keys
- Use of insecure functions (e.g., `eval()`, `exec()`)
- SQL injection vulnerabilities
- Weak cryptographic practices
- Shell injection risks
- Insecure deserialization

**Configuration** (.bandit):
```yaml
tests:
  - B201  # flask_debug_true
  - B501  # request_with_no_cert_validation
  - B502  # ssl_with_bad_version
  - B503  # ssl_with_bad_defaults
  - B506  # yaml_load
  - B601  # paramiko_calls
  - B602  # shell_with_shell_equals_true

exclude_dirs:
  - /venv/
  - /env/
  - /migrations/
  - /staticfiles/
```

#### 2. Safety - Dependency Vulnerability Scanner
**Purpose**: Check dependencies for known security vulnerabilities

```bash
# Installation
pip install safety

# Check installed packages
safety check

# Check requirements file
safety check -r requirements.txt

# Generate JSON report
safety check --json > safety-report.json

# Only show vulnerabilities (ignore warnings)
safety check --output bare
```

**What it detects**:
- Known vulnerabilities in dependencies (CVE database)
- Outdated packages with security patches
- Dependencies with security advisories

**Best Practices**:
- Run weekly or on dependency updates
- Integrate into CI pipeline
- Update vulnerable packages immediately
- Use `pip-audit` as alternative/complement

#### 3. pip-audit - Official Python Vulnerability Scanner
**Purpose**: Scan Python dependencies for known vulnerabilities

```bash
# Installation
pip install pip-audit

# Scan current environment
pip-audit

# Scan requirements file
pip-audit -r requirements.txt

# Generate detailed report
pip-audit --desc

# Fix issues automatically
pip-audit --fix
```

**Advantages over Safety**:
- Official Python Packaging Authority tool
- Uses PyPI's vulnerability database
- More up-to-date vulnerability data
- Can suggest fixes

#### 4. Semgrep - Advanced Static Analysis
**Purpose**: Find bugs and enforce code standards

```bash
# Installation
pip install semgrep

# Run with Python ruleset
semgrep --config=p/python

# Django-specific rules
semgrep --config=p/django

# Security-focused scan
semgrep --config=p/security-audit

# Custom rules
semgrep --config=.semgrep.yml calendar_app/
```

**What it detects**:
- Security vulnerabilities
- Bug patterns
- Code quality issues
- Framework-specific problems (Django, Flask, etc.)

**Rulesets**:
- `p/python`: General Python issues
- `p/django`: Django-specific vulnerabilities
- `p/security-audit`: Security-focused checks
- `p/owasp-top-ten`: OWASP Top 10 vulnerabilities

#### 5. Django Security Checklist Tool
**Purpose**: Check Django settings against security best practices

```bash
# Run checks
cd meeting_scheduler
python manage.py check --deploy

# Django's built-in security checks
python manage.py check --tag security
```

**What it checks**:
- DEBUG mode in production
- SECRET_KEY configuration
- ALLOWED_HOSTS settings
- HTTPS/SSL configuration
- Session/cookie security
- CSRF settings

#### 6. Detect-Secrets - Secret Detection
**Purpose**: Prevent secrets from being committed to Git

```bash
# Installation
pip install detect-secrets

# Scan for secrets
detect-secrets scan

# Create baseline
detect-secrets scan > .secrets.baseline

# Audit found secrets
detect-secrets audit .secrets.baseline
```

**What it detects**:
- API keys
- Passwords
- Private keys
- AWS credentials
- GitHub tokens

---

## Common Vulnerabilities

### OWASP Top 10 (2021) - Django Context

#### 1. Broken Access Control
**Risk**: Users accessing resources they shouldn't

**Prevention**:
```python
# Use Django's permission system
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

@login_required
def edit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    # Additional check: user owns the group
    if group.created_by != request.user:
        raise PermissionDenied("You can only edit groups you created")

    # ... edit logic
```

**Testing**:
- Test unauthorized access attempts
- Verify permission checks
- Test horizontal privilege escalation (user A accessing user B's data)

#### 2. Cryptographic Failures
**Risk**: Sensitive data exposed due to weak encryption

**Prevention**:
```python
# Use Django's password hashers (PBKDF2 by default)
from django.contrib.auth.hashers import make_password, check_password

# NEVER store plain text passwords
password_hash = make_password('user_password')

# For sensitive data at rest, use cryptography library
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)
encrypted = cipher.encrypt(b"sensitive data")
```

**Requirements**:
- Always use HTTPS in production
- Use strong password hashing (Django's default is good)
- Encrypt sensitive data at rest
- Use TLS 1.2+ for connections

#### 3. Injection
**Risk**: Malicious code executed via untrusted input

**Prevention**:
```python
# Django ORM prevents SQL injection
# GOOD
users = User.objects.filter(username=untrusted_input)

# BAD - Never use raw SQL with user input
cursor.execute(f"SELECT * FROM users WHERE username = '{untrusted_input}'")

# If raw SQL necessary, use parameterization
cursor.execute(
    "SELECT * FROM users WHERE username = %s",
    [untrusted_input]
)

# Command injection prevention
# BAD
os.system(f"ls {user_input}")

# GOOD
import subprocess
subprocess.run(['ls', user_input], check=True)  # Shell=False by default
```

**Testing**:
- Test with SQL injection payloads (`' OR '1'='1`)
- Test with command injection (`; rm -rf /`)
- Test with XSS payloads (`<script>alert('XSS')</script>`)

#### 4. Insecure Design
**Risk**: Architectural flaws in security design

**Prevention**:
- Threat modeling during design phase
- Security requirements from start
- Principle of least privilege
- Defense in depth
- Secure defaults

**Example - Data Isolation**:
```python
# Ensure users can only access their own data
@login_required
def calendar_view(request):
    """Display user's personal calendar."""
    # Only show current user's unavailability entries
    unavailabilities = Unavailability.objects.filter(
        user=request.user
    ).order_by('-date', '-start_time')

    return render(request, 'calendar_app/calendar.html', {
        'unavailabilities': unavailabilities
    })
```

#### 5. Security Misconfiguration
**Risk**: Insecure default configurations

**Prevention**:
```python
# settings.py - Production configuration

# NEVER leave DEBUG=True in production
DEBUG = False

# Use strong SECRET_KEY from environment
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured('SECRET_KEY must be set')

# Restrict ALLOWED_HOSTS
ALLOWED_HOSTS = [
    'your-domain.com',
    'www.your-domain.com',
]

# Security headers
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
```

**Check**:
```bash
cd meeting_scheduler
python manage.py check --deploy
```

#### 6. Vulnerable and Outdated Components
**Risk**: Using libraries with known vulnerabilities

**Prevention**:
```bash
# Regularly update dependencies
pip list --outdated

# Check for vulnerabilities
safety check
pip-audit

# Update vulnerable packages
pip install --upgrade package-name

# Use dependabot or renovate bot for automated updates
```

**Requirements**:
- Update dependencies monthly minimum
- Security patches immediately
- Test after updates
- Pin versions in requirements.txt

#### 7. Identification and Authentication Failures
**Risk**: Weak authentication mechanisms

**Prevention**:
```python
# Implement comprehensive authentication security

# 1. Strong password requirements
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 2. Secure sessions
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
SESSION_COOKIE_AGE = 3600  # 1 hour timeout

# 3. Secure password reset
# - Use token-based reset
# - Time-limited tokens (1 hour)
# - Single use tokens
```

#### 8. Software and Data Integrity Failures
**Risk**: Insecure CI/CD, updates, or deserialization

**Prevention**:
```python
# Never use pickle with untrusted data
# BAD
import pickle
data = pickle.loads(untrusted_data)

# GOOD
import json
data = json.loads(untrusted_data)

# Verify signatures on updates
# Check integrity of dependencies
pip install --require-hashes -r requirements.txt

# Use hash verification in requirements.txt
# package==1.0.0 --hash=sha256:abcd1234...
```

#### 9. Security Logging and Monitoring Failures
**Risk**: Attacks go undetected

**Prevention**:
```python
# Comprehensive security logging
import logging
logger = logging.getLogger(__name__)

# Log all authentication events
logger.info('Successful login: %s', username)
logger.warning('Failed login attempt for username: %s', username)

# Log security-relevant changes
logger.info('Password changed for user: %s', username)
logger.warning('Unauthorized access attempt to group: %s by user: %s', group_id, username)

# Log input validation failures
logger.warning('Invalid date format submitted: %s', date_string)
```

**Requirements**:
- Log all authentication events (success and failure)
- Log authorization failures
- Log input validation failures
- Log application errors
- Protect logs from tampering
- Regular log review

#### 10. Server-Side Request Forgery (SSRF)
**Risk**: Server makes requests to unintended destinations

**Prevention**:
```python
# Validate URLs before making requests
from urllib.parse import urlparse
import requests

ALLOWED_DOMAINS = ['api.example.com', 'data.example.com']

def fetch_external_data(url):
    """Fetch data from external source with SSRF protection."""
    parsed = urlparse(url)

    # Check protocol
    if parsed.scheme not in ['http', 'https']:
        raise ValueError("Only HTTP/HTTPS allowed")

    # Check domain whitelist
    if parsed.netloc not in ALLOWED_DOMAINS:
        raise ValueError("Domain not in whitelist")

    # Make request
    response = requests.get(url, timeout=5)
    return response.content
```

---

## Input Validation

### Validation Principles
1. **Validate on Server Side**: Never trust client-side validation
2. **Whitelist, Don't Blacklist**: Define what IS allowed
3. **Validate Early**: Check input before processing
4. **Fail Securely**: Reject invalid input
5. **Sanitize Output**: Encode for context (HTML, SQL, etc.)

### Django Form Validation
```python
from django import forms
from django.core.validators import EmailValidator, RegexValidator
from datetime import datetime, time

class UnavailabilityForm(forms.Form):
    """Secure unavailability form with comprehensive validation."""

    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Date of unavailability"
    )

    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        help_text="Start time (24-hour format)"
    )

    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        help_text="End time (24-hour format)"
    )

    description = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Optional description'})
    )

    def clean(self):
        """Validate time range and date."""
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        # Validate date is not in past
        if date and date < datetime.date.today():
            raise forms.ValidationError('Cannot create entries for past dates')

        # Validate time range
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError('Start time must be before end time')

        return cleaned_data
```

### Input Validation Best Practices
```python
def validate_date_range(start_date, end_date):
    """
    Validate date range is logical.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        True if valid

    Raises:
        ValidationError: If range is invalid
    """
    # Validate dates exist
    if not start_date or not end_date:
        raise ValidationError('Both dates are required')

    # Validate start is before end
    if start_date > end_date:
        raise ValidationError('Start date must be before or equal to end date')

    # Validate not too far in future (1 year max)
    max_date = datetime.date.today() + timedelta(days=365)
    if end_date > max_date:
        raise ValidationError('Cannot schedule more than 1 year in advance')

    return True
```

---

## Authentication & Authorization

### Authentication Best Practices
```python
# 1. Use Django's built-in authentication
from django.contrib.auth import authenticate, login, logout

# 2. Log all authentication events
import logging
logger = logging.getLogger(__name__)

@login_required
def calendar_view(request):
    """Protected view - requires authentication."""
    logger.info('User %s accessed calendar', request.user.username)
    # ... view logic

# 3. Use secure sessions
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection

# 4. Implement password requirements
AUTH_PASSWORD_VALIDATORS = [...]
```

### Authorization Patterns
```python
# Method 1: Decorator-based
from django.contrib.auth.decorators import login_required

@login_required
def protected_view(request):
    """Only authenticated users can access."""
    pass

# Method 2: Object-level permissions
@login_required
def delete_unavailability(request, entry_id):
    """Delete unavailability entry."""
    entry = get_object_or_404(Unavailability, id=entry_id)

    # Check ownership
    if entry.user != request.user:
        raise PermissionDenied("You can only delete your own entries")

    entry.delete()
    return redirect('calendar')

# Method 3: Group ownership
@login_required
def delete_group(request, group_id):
    """Delete group (owner only)."""
    group = get_object_or_404(Group, id=group_id)

    # Check ownership
    if group.created_by != request.user:
        raise PermissionDenied("You can only delete groups you created")

    group.delete()
    return redirect('group_list')
```

---

## Data Protection

### Sensitive Data Handling
```python
# 1. Identify sensitive data
# - Passwords
# - Email addresses
# - Session tokens
# - CSRF tokens
# - Personal schedule information

# 2. Never log sensitive data
# BAD
logger.info(f'User password: {password}')

# GOOD
logger.info('Password changed for user: %s', username)

# 3. Use environment variables
import os
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# 4. Use HTTPS for data in transit (always in production)
SECURE_SSL_REDIRECT = True
```

### Database Security
```python
# 1. Use parameterized queries (Django ORM does this)
Unavailability.objects.filter(user=request.user)  # Safe

# 2. Limit database permissions
# - Application user should not be database superuser
# - Grant only necessary permissions (SELECT, INSERT, UPDATE, DELETE)
# - No CREATE, DROP, ALTER in production

# 3. Data isolation - users only see their own data
unavailabilities = Unavailability.objects.filter(user=request.user)
groups = Group.objects.filter(members=request.user)
```

---

## Logging & Monitoring

### What to Log
```python
import logging
logger = logging.getLogger(__name__)

# Security Events (MUST LOG)
logger.info('Successful login: %s', username)
logger.warning('Failed login attempt for username: %s', username)
logger.warning('Password reset requested for email: %s', email)
logger.info('Password changed for user: %s', username)
logger.warning('Unauthorized access attempt to group %s by user %s', group_id, username)

# Application Errors (SHOULD LOG)
logger.error('Database error: %s', exception_type)
logger.warning('Invalid form submission: %s', form.errors)

# Debug Information (development only)
if settings.DEBUG:
    logger.debug('Processing calendar view for user %s', username)
```

### What NOT to Log
```python
# NEVER LOG:
# - Passwords (plaintext or hashed)
# - Session IDs
# - CSRF tokens
# - Full credit card numbers
# - Social security numbers

# BAD
logger.info(f'User {username} logged in with password {password}')

# GOOD
logger.info('User %s logged in successfully', username)
```

### Log Analysis
- Review logs weekly minimum
- Set up alerts for:
  - Multiple failed login attempts from same user
  - Unauthorized access attempts
  - Privilege escalation attempts
  - Unusual access patterns
- Use log aggregation tools (ELK stack, Splunk, etc.)

---

## Dependencies & Supply Chain

### Dependency Management
```bash
# 1. Pin exact versions in requirements.txt
Django==5.1.13
hypothesis==6.143.12

# 2. Regular updates
pip list --outdated

# 3. Security audits
safety check
pip-audit

# 4. Update immediately for security patches
pip install --upgrade package-name

# 5. Review dependency tree
pip install pipdeptree
pipdeptree
```

### Supply Chain Security
```bash
# 1. Verify package integrity
pip install --require-hashes -r requirements.txt

# 2. Use trusted sources only
# - PyPI official repository
# - Verify package authors
# - Check download statistics
# - Review GitHub stars/activity

# 3. Automated dependency updates
# - Use Dependabot (GitHub)
# - Use Renovate Bot
# - Review updates before merging

# 4. License compliance
pip-licenses
```

---

## Security Testing

### Automated Security Tests
```python
# calendar_app/tests.py

class SecurityTestCase(TestCase):
    """Security-focused test cases."""

    def setUp(self):
        """Set up test user and data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )

    def test_unauthorized_access_denied(self):
        """Test non-logged-in user cannot access protected pages."""
        response = self.client.get('/calendar/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_user_cannot_access_other_user_data(self):
        """Test users can only see their own data."""
        self.client.login(username='testuser', password='testpass123')

        # Create entry for other user
        other_unavail = Unavailability.objects.create(
            user=self.other_user,
            date=datetime.date.today(),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0)
        )

        # testuser should not see other_unavail in their calendar
        response = self.client.get('/calendar/')
        self.assertNotContains(response, 'otheruser')

    def test_csrf_protection_enforced(self):
        """Test CSRF token required for POST requests."""
        self.client.login(username='testuser', password='testpass123')

        # POST without CSRF token should fail
        response = self.client.post('/calendar/', {
            'date': datetime.date.today(),
            'start_time': '09:00',
            'end_time': '10:00'
        })
        self.assertEqual(response.status_code, 403)
```

### Manual Security Testing
```bash
# 1. Use OWASP ZAP for automated scanning
# Download from: https://www.zaproxy.org/

# 2. Test common vulnerabilities
# - SQL injection
# - XSS (reflected, stored, DOM-based)
# - CSRF
# - Authentication bypass
# - Authorization bypass
# - Session management

# 3. Fuzz testing
# Use hypothesis for property-based testing (already implemented)
cd meeting_scheduler
python manage.py test calendar_app.test_fuzz
```

### Penetration Testing
- Conduct annual penetration tests
- Test in staging environment
- Fix vulnerabilities before production deployment

---

## Bug Detection Strategies

### Static Analysis Tools

#### Pylint (already implemented)
```bash
cd meeting_scheduler
pylint calendar_app/*.py --disable=C0114,C0115,C0116,R0903,R0914,R0912,R0915,E1101 --max-line-length=120
```
**Catches**: Code quality issues, potential bugs, bad practices

#### Mypy - Type Checking
```bash
pip install mypy
mypy calendar_app/
```
**Catches**: Type errors, inconsistent return types, incorrect function calls

### Dynamic Analysis

#### Coverage.py - Code Coverage
```bash
cd meeting_scheduler
coverage run --source=calendar_app manage.py test calendar_app.tests
coverage report
coverage html  # Generate HTML report
```
**Purpose**: Find untested code paths

#### Hypothesis - Property-Based Testing (already implemented)
```python
from hypothesis import given
from hypothesis.strategies import dates, times

@given(dates(), times(), times())
def test_unavailability_with_random_times(test_date, start, end):
    """Test unavailability with randomly generated times."""
    # Test with randomly generated inputs
    # Already implemented in test_fuzz.py
```
**Purpose**: Find edge cases through fuzzing

#### Mutation Testing (already implemented)
```bash
cd meeting_scheduler
python run_mutation_test.py
```
**Purpose**: Verify tests actually catch bugs (100% score achieved)

### Code Review
- All code must be reviewed before merge
- Use security checklist
- Look for common vulnerabilities
- Verify input validation
- Check error handling

---

## Incident Response

### Preparation
1. **Security Contacts**: Designate security response team
2. **Communication Plan**: How to report and escalate issues
3. **Documentation**: Keep this guide updated
4. **Backups**: Regular backups of database and code

### Detection
1. **Monitor Logs**: Regular log review
2. **Alerts**: Set up automated alerts
3. **User Reports**: Provide security reporting mechanism
4. **Vulnerability Scans**: Regular automated scans

### Response Procedure
1. **Assess**: Determine severity and scope
2. **Contain**: Isolate affected systems
3. **Eradicate**: Remove the threat
4. **Recover**: Restore normal operations
5. **Document**: Record timeline and actions
6. **Learn**: Post-incident review

### Security Incident Severity

#### Critical (P0) - Immediate Response
- Data breach
- Remote code execution
- Authentication bypass
- Database compromise

**Action**: Take system offline if needed, patch immediately

#### High (P1) - 24 Hour Response
- SQL injection vulnerability
- XSS vulnerability
- Privilege escalation
- Sensitive data exposure

**Action**: Create emergency patch, deploy ASAP

#### Medium (P2) - 1 Week Response
- Information disclosure
- CSRF vulnerability
- Outdated dependencies with known issues

**Action**: Schedule fix in next sprint

#### Low (P3) - Next Sprint
- Security misconfiguration
- Missing security headers
- Deprecated functionality

**Action**: Add to backlog

---

## Security Checklist

### Before Deployment
- [ ] DEBUG = False in production
- [ ] SECRET_KEY from environment variable
- [ ] ALLOWED_HOSTS configured
- [ ] HTTPS enforced (SECURE_SSL_REDIRECT = True)
- [ ] Secure cookies enabled
- [ ] CSRF protection enabled
- [ ] XSS protection enabled
- [ ] SQL injection protection verified
- [ ] Input validation on all user inputs
- [ ] Password requirements enforced
- [ ] Security headers configured
- [ ] Error pages don't expose sensitive info
- [ ] Logging configured and working
- [ ] Dependencies up to date
- [ ] Security scan passed (Bandit, pip-audit)
- [ ] All 141 tests passing
- [ ] Code review completed

### Regular Maintenance (Monthly)
- [ ] Review security logs
- [ ] Update dependencies
- [ ] Run security scans (Bandit, pip-audit, Semgrep)
- [ ] Review access controls
- [ ] Test backup restoration
- [ ] Review incident response plan
- [ ] Update security documentation

### After Security Incident
- [ ] Patch vulnerability
- [ ] Update tests to prevent regression
- [ ] Review related code for similar issues
- [ ] Update security documentation
- [ ] Communicate to team
- [ ] Post-incident review meeting

---

## Security Scanning Integration

### Local Security Scanning

**Run all scans locally:**
```bash
cd meeting_scheduler

# 1. Bandit - Python security linting
bandit -r calendar_app/ -c .bandit

# 2. pip-audit - Dependency vulnerability scanning
pip-audit

# 3. Django security check
python manage.py check --deploy

# 4. Semgrep - Advanced static analysis (optional)
semgrep --config=p/django calendar_app/
```

### CI/CD Integration

Security scans are run automatically on all pull requests via GitHub Actions. The CI pipeline includes:

1. **Code Quality** (Pylint)
2. **All Tests** (141 tests)
3. **Security Scans** (Bandit, pip-audit)
4. **Coverage Report**

See `.github/workflows/` for CI configuration.

---

## Resources

### Documentation
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

### Tools
- [Bandit](https://bandit.readthedocs.io/)
- [Safety](https://pyup.io/safety/)
- [pip-audit](https://github.com/pypa/pip-audit)
- [Semgrep](https://semgrep.dev/)
- [OWASP ZAP](https://www.zaproxy.org/)

### Training
- [OWASP WebGoat](https://owasp.org/www-project-webgoat/)
- [Hack The Box](https://www.hackthebox.com/)
- [PentesterLab](https://pentesterlab.com/)

---

## Changelog

### Version 2.0 (January 11, 2025)
- Updated for Meeting Scheduler project (CS3300)
- Updated current security implementations to match calendar_app
- Updated file paths and examples (calendar_app/, meeting_scheduler/)
- Updated test statistics (141 tests, 93%+ coverage, 100% mutation score)
- Removed outdated Sprint 3 implementation plan
- Added Meeting Scheduler-specific examples
- Integrated with current CI/CD pipeline

### Version 1.0 (October 29, 2024)
- Initial security guide creation
- Documented baseline security implementations
- Added security scanning tool recommendations
- Integrated with STYLE_GUIDE.md and CLAUDE.md

---

**Security Questions or Concerns?**
Report security issues privately to the project team. For the CS3300 course project, contact the course instructors or project team leads.

**Project Team**: CS3300 Meeting Scheduler Development Team
