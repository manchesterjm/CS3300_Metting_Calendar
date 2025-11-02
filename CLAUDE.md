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

**IMPORTANT: All tests (unit, fuzz, and mutation) MUST be run every time code is updated.**

### Required Testing Process

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
- Fix ALL pylint findings before proceeding to tests
- Ensure code quality standards are met
- Re-run pylint after fixes to verify all issues resolved

#### Step 2: Run Unit Tests
```bash
python manage.py test calendar_app.tests --verbosity=2
```

**Action Required:**
- If ANY test fails, fix the error immediately
- Re-run tests after each fix
- Continue until ALL 21 tests pass

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

**Expected Result:** All 30 tests (21 unit + 9 fuzz) must pass

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
- Overall coverage should be 70%+

### Quick Test Commands

**🚀 RECOMMENDED: Run automated test suite (all steps in order):**
```bash
python run_all_tests.py
```
This script automatically runs all 6 steps in order and stops at the first failure.

**Run all tests in one command:**
```bash
python manage.py test calendar_app && python run_mutation_test.py
```

**Full quality check (Pylint + All Tests + Coverage):**
```bash
pylint calendar_app/*.py --disable=C0114,C0115,C0116,R0903,R0914,R0912,R0915,E1101 --max-line-length=120 && \
coverage run --source=calendar_app manage.py test calendar_app && \
coverage report && \
python run_mutation_test.py
```

**Generate HTML coverage report:**
```bash
coverage html  # Report in htmlcov/index.html
```

### Testing Standards

**All code changes MUST meet these criteria before being considered complete:**

✅ Pylint score: 9.0+ (or all issues fixed)
✅ Unit tests: 21/21 passing
✅ Fuzz tests: 9/9 passing
✅ Total tests: 30/30 passing
✅ Mutation score: 100%
✅ Code coverage: 93%+ on critical modules
✅ No test failures or errors

**If any test fails:**
1. DO NOT proceed to next test type
2. Fix the error immediately
3. Re-run the failed test
4. Repeat until test passes
5. Then continue to next test type

### Current Test Statistics
- Unit tests: 21 tests covering models, forms, and views
- Fuzz tests: 9 tests with ~350 generated test cases
- Total test cases: 30 tests + 350 fuzz-generated cases
- Code coverage: 93%+ on critical modules (models, forms, views), 70% overall
- Mutation score: 100% (8/8 mutations killed)
- Test execution time: ~1-2 seconds

## Architecture Notes

### Single-View Application
The entire application uses a single view function `calendar_view` in `calendar_app/views.py` that handles multiple POST actions via button names:

- `submit_unavailability`: Adds new unavailability records to the database
- `show_free_times`: Calculates free 30-minute slots between 8:00-20:00 based on unavailability
- `show_last_five`: Displays the 5 most recent unavailability entries
- `delete_selected`: Deletes selected unavailability entries

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
- Single model: `Unavailability` with date, start_time, end_time fields
- No user authentication system (all data is global)

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
- **Django Version**: 5.1.6
- **Database**: SQLite3 at `BASE_DIR / 'db.sqlite3'`
- **Debug Mode**: `DEBUG = True` (development only)
- **Allowed Hosts**: Currently `['*']` (accepts all hosts). For production or VM deployment, update to specific IP addresses:
  ```python
  ALLOWED_HOSTS = ['128.198.51.79', 'localhost']  # Example
  ```
- **Secret Key**: Currently uses insecure default key (change for production)
- **Time Zone**: UTC
- **Installed Apps**: Only `calendar_app` beyond Django defaults
- **Auto-reload**: With `DEBUG=True`, Django automatically reloads when files are modified

## Code Attribution

Comments in the codebase indicate:
- Django templates and standard files were adapted from course material (CS 2080)
- ChatGPT was used for troubleshooting code syntax
- Most customization focused on form handling and database operations
