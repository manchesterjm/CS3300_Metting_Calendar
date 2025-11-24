# GitHub Issues to Create

Copy and paste these into GitHub Issues manually, or use the GitHub CLI if available.

---

## Issue 1: Security - Change password generation from GET to POST

**Labels**: `security`, `critical`

**Title**: Security: Change password generation from GET to POST

**Body**:
```
**Priority**: Critical ⚠️

**AI Code Review Finding**: Password generation API uses GET requests which can leak sensitive data through server logs and browser history.

**Files to Fix**:
- `templates/admin/auth/user/change_password.html`
- `templates/calendar_app/change_password.html`
- `templates/calendar_app/password_reset_confirm.html`
- `templates/calendar_app/register.html`
- `calendar_app/auth_views.py`

**Required Changes**:
1. Update all fetch() calls to use POST method
2. Update `generate_password_api` view to accept POST
3. Verify CSRF protection works correctly
4. Add tests for POST method

**Reference**: `AI_CODE_REVIEW_FIXES.md` #1
```

---

## Issue 2: Django Best Practice - Remove null=True from CharField

**Labels**: `enhancement`, `high-priority`

**Title**: Django Best Practice: Remove null=True from CharField in models

**Body**:
```
**Priority**: Critical ⚠️

**AI Code Review Finding**: Django convention is to avoid `null=True` on string-based fields like CharField. Use `blank=True` with `default=''` instead.

**Files to Fix**:
- `calendar_app/models.py` (Unavailability.description, GroupUnavailability.description)
- New migration required

**Required Changes**:
```python
# Change from:
description = models.CharField(max_length=200, blank=True, null=True)

# To:
description = models.CharField(max_length=200, blank=True, default='')
```

**Migration Steps**:
1. Create data migration to convert NULL values to empty strings
2. Create schema migration to remove null=True
3. Update all tests that check for None values

**Reference**: `AI_CODE_REVIEW_FIXES.md` #2
```

---

## Issue 3: Error Handling - Replace broad Exception catching

**Labels**: `code-quality`, `high-priority`

**Title**: Error Handling: Replace broad Exception catching in email_backend

**Body**:
```
**Priority**: Critical ⚠️

**AI Code Review Finding**: Catching generic `Exception` obscures underlying issues during debugging.

**File to Fix**:
- `calendar_app/email_backend.py:57`

**Required Change**:
```python
# Change from:
except Exception as e:
    if not self.fail_silently:
        raise e
    return False

# To:
except (smtplib.SMTPException, OSError) as e:
    if not self.fail_silently:
        raise e
    return False
```

**Tests**: Add tests for specific exception types

**Reference**: `AI_CODE_REVIEW_FIXES.md` #3
```

---

## Issue 4: Code Duplication - Extract clean_description to base form

**Labels**: `refactoring`, `high-priority`

**Title**: Code Duplication: Extract clean_description validation to base form

**Body**:
```
**Priority**: High

**AI Code Review Finding**: Duplicate validation logic in multiple form classes.

**Files to Fix**:
- `calendar_app/forms.py` (UnavailabilityForm, GroupUnavailabilityForm)

**Required Changes**:
Create a base form class with shared validation logic:

```python
class BaseDescriptionForm(forms.Form):
    def clean_description(self):
        description = self.cleaned_data.get('description', '').strip()
        if len(description) > 200:
            raise forms.ValidationError('Description must be 200 characters or less.')
        return description

class UnavailabilityForm(BaseDescriptionForm, forms.ModelForm):
    # Remove duplicate clean_description method
    pass

class GroupUnavailabilityForm(BaseDescriptionForm, forms.ModelForm):
    # Remove duplicate clean_description method
    pass
```

**Reference**: `AI_CODE_REVIEW_FIXES.md` #4
```

---

## Issue 5: Missing Error Handling - Date parsing in views

**Labels**: `bug`, `high-priority`

**Title**: Missing Error Handling: Add date parsing validation in views

**Body**:
```
**Priority**: High

**AI Code Review Finding**: No error handling for invalid date formats. `strptime` will raise ValueError.

**Files to Fix**:
- `calendar_app/views.py:calendar_view`
- `calendar_app/group_views.py:group_calendar_view`

**Required Changes**:
```python
try:
    selected_date = datetime.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
except ValueError:
    messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
    return redirect('calendar')
```

**Tests**: Add tests for invalid date formats

**Reference**: `AI_CODE_REVIEW_FIXES.md` #5
```

---

## Issue 6: Missing POST Data Validation

**Labels**: `bug`, `high-priority`

**Title**: Missing POST Data Validation: Check for date field existence

**Body**:
```
**Priority**: High

**AI Code Review Finding**: Code assumes `selected_date_str` exists in POST data without checking.

**File to Fix**:
- `calendar_app/views.py:calendar_view`

**Required Change**:
```python
selected_date_str = request.POST.get('date')
if not selected_date_str:
    messages.error(request, 'Date is required.')
    return redirect('calendar')
```

**Tests**: Add tests for missing POST data

**Reference**: `AI_CODE_REVIEW_FIXES.md` #6
```

---

## Issue 7: Time Zone Handling

**Labels**: `enhancement`, `high-priority`

**Title**: Time Zone Handling: Add timezone support to calculate_free_time_slots

**Body**:
```
**Priority**: High

**AI Code Review Finding**: Function doesn't consider time zone information, could lead to incorrect calculations.

**File to Fix**:
- `calendar_app/utils.py:calculate_free_time_slots`

**Required Changes**:
```python
from django.utils import timezone

def calculate_free_time_slots(selected_date, unavail_list):
    # Use timezone-aware datetime objects
    start_dt = timezone.make_aware(
        datetime.combine(selected_date, datetime.min.time().replace(hour=8))
    )
    # ... rest of function
```

**Configuration**:
- Ensure `USE_TZ = True` in settings.py
- Set appropriate `TIME_ZONE` in settings.py

**Reference**: `AI_CODE_REVIEW_FIXES.md` #7
```

---

## Issue 8: Extract JavaScript to External Files

**Labels**: `refactoring`, `medium-priority`

**Title**: Extract JavaScript to External Files

**Body**:
```
**Priority**: Medium

**AI Code Review Finding**: JavaScript embedded in HTML reduces maintainability and prevents browser caching.

**Files to Refactor**:
- All templates with inline JavaScript

**Required Changes**:
1. Create `static/calendar_app/js/` directory
2. Extract JavaScript to separate files:
   - `password_generation.js`
   - `csrf_utils.js`
3. Update templates to use `{% static %}` tags
4. Implement Content Security Policy (CSP)

**Benefits**:
- Browser caching
- Easier testing
- Better security (CSP)
- Code reusability

**Reference**: `AI_CODE_REVIEW_FIXES.md` #8
```

---

## Issue 9: User Feedback for Empty free_times

**Labels**: `ui/ux`, `medium-priority`

**Title**: User Feedback: Show message when free_times is empty

**Body**:
```
**Priority**: Medium

**AI Code Review Finding**: No message shown when `free_times` is empty list, leaving users confused.

**Files to Fix**:
- `templates/calendar_app/calendar.html`
- `templates/calendar_app/group_calendar.html`

**Required Change**:
```django
{% if free_times %}
    <ul>
        {% for time in free_times %}
            <li>{{ time }}</li>
        {% endfor %}
    </ul>
{% else %}
    <p style="color: #27ae60; font-weight: bold;">
        🎉 All time slots are free! No unavailability entries for this date.
    </p>
{% endif %}
```

**Reference**: `AI_CODE_REVIEW_FIXES.md` #9
```

---

## Issue 10: Admin Customization Conflicts

**Labels**: `documentation`, `medium-priority`

**Title**: Admin Customization: Document or refactor User admin pattern

**Body**:
```
**Priority**: Medium

**AI Code Review Finding**: Unregister/re-register pattern for User admin could conflict with other apps.

**File to Review**:
- `calendar_app/admin.py`

**Options**:
1. Use a custom user model instead (recommended long-term)
2. Coordinate admin customizations in single location
3. Document the approach and potential conflicts

**Immediate Action**:
Add detailed documentation in code comments explaining:
- Why this pattern is needed
- What conflicts could arise
- How to resolve conflicts if they occur

**Reference**: `AI_CODE_REVIEW_FIXES.md` #10
```

---

## Issue 11: JavaScript Testing

**Labels**: `testing`, `medium-priority`

**Title**: JavaScript Testing: Add tests for JavaScript functions

**Body**:
```
**Priority**: Medium

**AI Code Review Finding**: No tests for JavaScript functions (getCookie, generatePassword, etc.)

**Required Changes**:
1. Set up Jest or similar JavaScript testing framework
2. Create test files for each JavaScript module:
   - `test_password_generation.js`
   - `test_csrf_utils.js`
3. Add to CI/CD pipeline
4. Aim for >80% JavaScript code coverage

**Functions to Test**:
- `getCookie(name)`
- `generatePassword()`
- `generatePasswordChange()`
- `generatePasswordReset()`
- `generateAdminPassword()`

**Reference**: `AI_CODE_REVIEW_FIXES.md` #11
```

---

## Issue 12: Split tests.py into Multiple Modules

**Labels**: `refactoring`, `low-priority`

**Title**: Split tests.py into Multiple Modules

**Body**:
```
**Priority**: Low

**AI Code Review Finding**: File is large (~1350 lines) and disables `too-many-lines` pylint warning.

**File to Split**:
- `calendar_app/tests.py`

**Proposed Structure**:
```
calendar_app/tests/
├── __init__.py
├── test_models.py
├── test_forms.py
├── test_views.py
├── test_auth.py
└── test_groups.py
```

**Benefits**:
- Better organization
- Easier to navigate
- Faster parallel test execution
- Reduced cognitive load

**Reference**: `AI_CODE_REVIEW_FIXES.md` #14
```

---

## Instructions for Creating Issues

### Using GitHub Web Interface:
1. Go to https://github.com/manchesterjm/CS3300_Metting_Calendar/issues/new
2. Copy the Title from above
3. Copy the Body from above
4. Add the specified Labels
5. Click "Submit new issue"
6. Repeat for each issue

### Using GitHub CLI (if installed):
```bash
# Install GitHub CLI if needed: https://cli.github.com/

# Then run these commands:
cd C:\CS3300_project

gh issue create --title "Security: Change password generation from GET to POST" --label "security,critical" --body-file <(echo "See GITHUB_ISSUES_TO_CREATE.md Issue 1")

# Repeat for each issue...
```

---

**Total Issues to Create**: 12
**Critical**: 3
**High Priority**: 4
**Medium Priority**: 4
**Low Priority**: 1
