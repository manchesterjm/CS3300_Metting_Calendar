# Meeting Scheduler

**CS3300 Course Project - Django-based Meeting Scheduler Application**

A comprehensive web application for managing personal schedules and finding common free times within groups.

[![Django](https://img.shields.io/badge/Django-5.1.13-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-141%20passing-brightgreen.svg)](./meeting_scheduler/TESTING_REPORT.md)
[![Coverage](https://img.shields.io/badge/Coverage-93%25-brightgreen.svg)](./meeting_scheduler/TESTING_REPORT.md)
[![Mutation Score](https://img.shields.io/badge/Mutation%20Score-100%25-brightgreen.svg)](./meeting_scheduler/TESTING_REPORT.md)
[![Pylint](https://img.shields.io/badge/Pylint-9.98%2F10-brightgreen.svg)](./CLAUDE.md)
[![Security](https://img.shields.io/badge/Security-0%20vulnerabilities-brightgreen.svg)](./CLAUDE.md)

---

## 🎯 Overview

Meeting Scheduler helps users manage their availability and coordinate schedules with groups. Users maintain personal calendars showing when they're unavailable, and the system automatically calculates common free times when viewing group calendars.

**Key Concept:**
- Users manage their schedules on their **personal calendar** (`/calendar/`)
- Groups view **read-only aggregated calendars** (`/groups/X/calendar/`) showing common free times
- No manual group calendar management - it's automatically calculated from members' personal calendars

---

## ✨ Features

### 🗓️ Personal Calendar Management
- **Add Unavailability**: Mark times when you're not available
- **Optional Descriptions**: Add notes to entries (e.g., "Doctor appointment", "Meeting")
- **View Free Times**: See available 30-minute slots for any date (8:00 AM - 8:00 PM)
- **Last 5 Entries**: Quick view of recent unavailability entries
- **Bulk Delete**: Select and delete multiple entries at once
- **User-Specific**: Each user only sees their own calendar data

### 👥 Group Collaboration
- **Create Groups**: Form scheduling groups with team members
- **Join with Code**: Easy onboarding with 8-character join codes (e.g., `AB2C3DEF`)
  - Group admins generate shareable codes
  - Users join instantly by entering the code
  - Codes can be enabled/disabled or regenerated
- **Add Members**: Invite users to your group by username
- **Read-Only Group Calendar**: View common free times for all group members
  - Automatically aggregates all members' personal calendars
  - Shows times when **everyone** is available
  - No manual entry needed - updates automatically
- **Group Management**: Owners can add/remove members and delete groups

### 🔐 Authentication & Security
- **User Registration**: Create accounts with email validation
- **Login/Logout**: Secure session-based authentication
- **Account Management**: Update profile information
- **Password Reset**: Email-based password recovery
- **Admin Access**: Staff users can access Django admin panel
- **Data Isolation**: Users can only access their own data
- **Rate Limiting**: Protection against brute force attacks
- **Security Scanning**: Automated vulnerability detection

### 📧 Email Integration
- **Password Reset Emails**: Secure token-based password recovery
- **Gmail SMTP Support**: Configured for real email sending
- **Development Mode**: Console backend for local testing
- **Windows SSL Bypass**: Custom backend for Windows development

### 🎨 User Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern Styling**: Clean, professional interface
- **Navigation Banner**: Persistent header with user info and quick actions
- **Success Messages**: Clear feedback for all actions
- **Mobile-Optimized**: Touch-friendly buttons and stacked layouts

---

## 🗺️ Roadmap

### Planned Features

#### Phase 1: Enhanced Onboarding (In Progress)
- **🟡 Group Join Codes** - Generate shareable codes for easy group joining
  - Status: In Development
  - Target: November 2025

#### Phase 2: Schedule Automation (Next)
- **🔴 Recurring Unavailability** - Define repeating blocks (e.g., "Every Monday 9-5")
  - Status: Planned
  - Target: Q1 2026

#### Phase 3: Meeting Coordination (Future)
- **🔴 Meeting Proposals** - Propose specific meeting times with accept/decline workflow
  - Status: Planned
  - Target: Q2 2026

See [ROADMAP.md](./ROADMAP.md) for detailed feature specifications, timelines, and technical requirements.

---

## 🏗️ Architecture

### Application Structure
```
meeting_scheduler/
├── manage.py                    # Django management script
├── db.sqlite3                   # SQLite database
├── meeting_scheduler/           # Project configuration
│   ├── settings.py              # Django settings
│   ├── urls.py                  # Root URL routing
│   └── wsgi.py                  # WSGI application
└── calendar_app/                # Main application
    ├── models.py                # Unavailability, Group models
    ├── views.py                 # Personal calendar views
    ├── group_views.py           # Group calendar views (read-only)
    ├── auth_views.py            # Authentication views
    ├── forms.py                 # Form definitions
    ├── urls.py                  # URL routing
    ├── tests.py                 # Unit tests (93 tests)
    ├── test_fuzz.py             # Fuzz tests (16 tests)
    ├── test_debug_crud.py       # Debug tests
    ├── email_backend.py         # Custom email backend for Windows
    └── templates/               # HTML templates
```

### Database Models
- **User**: Django's built-in user model (authentication)
- **Unavailability**: Personal calendar entries (user's schedule)
  - Fields: user, date, start_time, end_time, description
- **Group**: Scheduling groups for team collaboration
  - Fields: name, created_by, members (many-to-many)
- **GroupUnavailability**: Legacy model (not currently used - read-only workflow)

### Calendar Workflow
1. **Personal Calendar** - Users add their unavailability
2. **Group Calendar** - Automatically shows common free times
3. **Free Time Calculation** - System finds slots when ALL members are available

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/manchesterjm/CS3300_Metting_Calendar.git
cd CS3300_Metting_Calendar

# Create and activate virtual environment
cd meeting_scheduler
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create default admin account
python manage.py create_default_admin

# Start development server
python manage.py runserver 0.0.0.0:8000
```

**Access the application:**
- Main app: http://localhost:8000/
- Admin panel: http://localhost:8000/admin/
- Default admin credentials: `admin` / `admin123` (⚠️ Change immediately!)

### Network Access (VM/Remote)
```bash
python manage.py runserver 0.0.0.0:8000
```
Access at: `http://<your-ip>:8000/`

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [CLAUDE.md](./CLAUDE.md) | **Primary development guide** - Setup, testing, security |
| [ROADMAP.md](./ROADMAP.md) | **Product roadmap** - Planned features and timeline |
| [STYLE_GUIDE.md](./STYLE_GUIDE.md) | Python/Django coding standards |
| [SECURITY_GUIDE.md](./SECURITY_GUIDE.md) | Security best practices and scanning tools |
| [PASSWORD_RESET_GUIDE.md](./PASSWORD_RESET_GUIDE.md) | Password reset testing instructions |
| [GIT_WORKFLOW.md](./meeting_scheduler/GIT_WORKFLOW.md) | Feature branch workflow and CI/CD |
| [TESTING_REPORT.md](./meeting_scheduler/TESTING_REPORT.md) | Test results and coverage analysis |
| [DEPLOYMENT.md](./meeting_scheduler/DEPLOYMENT.md) | Production deployment guide |

---

## 🧪 Testing

### Test Suite
- **141 total tests** (93 unit + 16 fuzz + 32 other)
- **100% mutation score** (8/8 mutations killed)
- **93%+ coverage** on critical modules
- **~2 second** execution time

### Run All Tests
```bash
cd meeting_scheduler
python run_all_tests.py
```

### Individual Test Suites
```bash
# Pylint (code quality)
pylint calendar_app/*.py --disable=C0114,C0115,C0116,R0903,R0914,R0912,R0915,E1101 --max-line-length=120

# Unit tests (93 tests)
python manage.py test calendar_app.tests --verbosity=2

# Fuzz tests (16 tests)
python manage.py test calendar_app.test_fuzz --verbosity=2

# Mutation tests (100% score)
python run_mutation_test.py

# Security scans
python run_security_scans.py
```

---

## 🔒 Security

### Security Features
- ✅ **Zero vulnerabilities** (pip-audit, Safety scans)
- ✅ **Django 5.1.13** (latest security patches)
- ✅ **CSRF protection** on all forms
- ✅ **XSS protection** with auto-escaping
- ✅ **SQL injection protection** via Django ORM
- ✅ **Secure sessions** (HttpOnly, SameSite, 1-hour timeout)
- ✅ **Security headers** (X-Frame-Options, Content-Type-Nosniff)
- ✅ **Input validation** on all user inputs
- ✅ **Rate limiting** on authentication endpoints

### Security Scanning
```bash
cd meeting_scheduler
python run_security_scans.py
```

Runs: Bandit, Safety, pip-audit, Semgrep

---

## 📊 Code Quality

### Metrics
- **Pylint Score**: 9.98/10
- **Code Coverage**: 93%+ on critical modules
- **Mutation Score**: 100%
- **Test Pass Rate**: 100% (141/141)
- **Security Vulnerabilities**: 0
- **Documentation**: Comprehensive docstrings

### Standards Enforced
- PEP 8 compliance (120-char line length)
- Google-style docstrings
- Type hints on functions
- Comprehensive error handling
- Security best practices

---

## 🌐 URL Structure

| URL | View | Description | Auth Required |
|-----|------|-------------|---------------|
| `/` | home_view | Landing page | Yes |
| `/calendar/` | calendar_view | Personal calendar | Yes |
| `/groups/` | group_list_view | List user's groups | Yes |
| `/groups/create/` | group_create_view | Create new group | Yes |
| `/groups/<id>/` | group_detail_view | Group details | Yes |
| `/groups/<id>/calendar/` | group_calendar_view | Read-only group calendar | Yes |
| `/groups/<id>/add-member/` | group_add_member_view | Add member (owner only) | Yes |
| `/groups/<id>/remove-member/<uid>/` | group_remove_member_view | Remove member | Yes |
| `/groups/<id>/delete/` | group_delete_view | Delete group (owner only) | Yes |
| `/login/` | login_view | User login | No |
| `/logout/` | logout_view | User logout | Yes |
| `/register/` | register_view | User registration | No |
| `/account/` | account_view | Account management | Yes |
| `/password-reset/` | (Django built-in) | Request password reset | No |
| `/admin/` | (Django admin) | Admin interface | Staff only |

---

## 🛠️ Configuration

### Environment Variables (Production)

Create a `.env` file or set environment variables:

```bash
# Required in production
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Email configuration (Gmail example)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Database (PostgreSQL example)
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### Development Settings
```python
# meeting_scheduler/settings.py
DEBUG = True
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

---

## 📦 Dependencies

### Core Dependencies
- **Django 5.1.13** - Web framework
- **Python 3.11+** - Programming language

### Development Dependencies
- **pylint 4.0+** - Code quality
- **hypothesis 6.143+** - Fuzz testing
- **coverage 7.11+** - Code coverage
- **pytest 8.4+** - Test runner

### Security Dependencies
- **bandit 1.8+** - Security linter
- **safety 3.6+** - Dependency scanner
- **pip-audit 2.9+** - Vulnerability checker
- **semgrep 1.142+** - Security pattern scanner

---

## 🚢 Deployment

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use environment variable for `SECRET_KEY`
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Use production database (PostgreSQL/MySQL)
- [ ] Configure email backend (SMTP)
- [ ] Run `python manage.py collectstatic`
- [ ] Set up web server (Nginx/Apache)
- [ ] Configure security headers
- [ ] Set up backups
- [ ] Run security scans

See [DEPLOYMENT.md](./meeting_scheduler/DEPLOYMENT.md) for detailed instructions.

---

## 🤝 Contributing

### Workflow
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and add tests
3. Run test suite: `python run_all_tests.py`
4. Commit changes with descriptive message
5. Push branch: `git push -u origin feature/your-feature`
6. Create Pull Request on GitHub
7. Wait for CI/CD checks to pass
8. Merge after approval

See [GIT_WORKFLOW.md](./meeting_scheduler/GIT_WORKFLOW.md) for complete workflow.

---

## 🎓 Course Information

**Course**: CS3300 - Software Engineering
**Institution**: University of Virginia
**Semester**: Fall 2025
**Project Type**: Team Project - Meeting Scheduler Application

---

## 📝 License

This project is for educational purposes as part of CS3300 coursework.

---

## 🙏 Acknowledgments

- **Django**: Web framework used for the application
- **Django Documentation**: Extensive reference material
- **Course Instructors**: CS3300 teaching team
- **Claude Code**: AI-assisted development tool

---

## 📞 Support

For questions or issues:
1. Check the [documentation](./CLAUDE.md)
2. Review the [testing guide](./meeting_scheduler/TESTING_REPORT.md)
3. Consult the [security guide](./SECURITY_GUIDE.md)
4. Open an issue on GitHub

---

**Last Updated**: January 2025
**Version**: 2.0 (Read-Only Group Calendar Release)
**Status**: ✅ Production Ready
