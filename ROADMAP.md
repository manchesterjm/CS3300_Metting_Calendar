# Product Roadmap - Meeting Scheduler

**Last Updated**: November 23, 2025

---

## 🎯 Vision

Transform the Meeting Scheduler from a "find free times" tool into a complete meeting coordination platform that makes scheduling effortless for teams and groups.

---

## 📋 Current Status (v1.0 - Production Ready)

### ✅ Completed Features
- Personal calendar management with unavailability tracking
- Group creation and member management
- **Group join codes** - Easy onboarding with shareable 8-char codes ⭐ NEW
- Read-only group calendars showing common free times
- User authentication and password reset
- Responsive mobile-friendly UI
- Email integration (console and SMTP)
- Comprehensive test suite (172 tests, 93% coverage, 100% mutation score)
- Production deployment documentation
- Security hardening (0 vulnerabilities)

**Status**: Production-ready with join codes feature

---

## 🚀 Planned Features

### Phase 1: Enhanced Onboarding & Usability ✅ COMPLETE

#### Feature 1: Group Join Codes ⭐ **[✅ COMPLETED - Nov 23, 2025]**
**Priority**: HIGH
**Effort**: 3 hours (actual)
**Status**: ✅ Complete

**Description**: Generate shareable codes to join groups without manual admin intervention.

**Implementation Summary**:
- ✅ Added `join_code` and `join_code_enabled` fields to Group model
- ✅ Created migration 0007 for new fields
- ✅ Implemented `generate_join_code()` utility (8-char alphanumeric, excludes ambiguous chars)
- ✅ Created `JoinGroupForm` with validation (uppercase normalization, whitespace stripping)
- ✅ Implemented three views: `join_group_view`, `generate_join_code_view`, `toggle_join_code_view`
- ✅ Created `/groups/join/` template with instructions and code input
- ✅ Enhanced group detail page with join code management section (copy, enable/disable, regenerate)
- ✅ Added "Join with Code" button to group list page
- ✅ Comprehensive tests: 15 new tests covering models, forms, and edge cases
- ✅ All 172 tests passing (124 unit + 48 fuzz/integration)
- ✅ Pylint score: 10.00/10
- ✅ Zero security vulnerabilities

**Features Delivered**:
- Group admins can generate/regenerate codes with one click
- Codes are 8 characters (e.g., `AB2C3DEF`), excluding confusing chars (0/O, 1/I)
- Users join via `/groups/join/` with simple code entry
- Copy-to-clipboard functionality built-in
- Codes can be enabled/disabled without regenerating
- Full error handling (invalid codes, disabled codes, duplicate memberships)
- Mobile-responsive UI with clear instructions

**Acceptance Criteria**: ✅ All Met
- ✅ Group admin can generate join code
- ✅ Users can join group via code
- ✅ Duplicate code prevention (unique constraint)
- ✅ Invalid code error handling
- ✅ Code can be regenerated
- ✅ Code can be disabled
- ✅ All tests passing with new feature

---

### Phase 2: Schedule Automation (Q1 2026)

#### Feature 2: Recurring Unavailability ⭐ **[PLANNED - NEXT]**
**Priority**: HIGH
**Effort**: Medium (4-6 hours)
**Status**: 🔴 Planned

**Description**: Define repeating unavailable blocks to eliminate manual weekly entry.

**User Story**:
- User creates unavailability: "Every Monday 9:00-17:00" (work hours)
- System automatically expands recurring entries for future dates
- User can edit/delete single occurrence or entire series
- Supports patterns: daily, weekly, monthly, custom days

**Technical Requirements**:
- Add `is_recurring` boolean to Unavailability model
- Add `recurrence_pattern` JSON field (frequency, days, end_date)
- Add `parent_recurring_id` ForeignKey (for expanded instances)
- Utility function to generate recurring instances
- UI: Checkbox "Make this recurring" + recurrence editor
- Background task or on-demand expansion for next 90 days
- Update calendar views to handle recurring entries
- Add "Edit Series" vs "Edit This Occurrence" logic

**Database Changes**:
```python
# Migration: Add to Unavailability model
is_recurring = models.BooleanField(default=False)
recurrence_pattern = models.JSONField(null=True, blank=True)
parent_recurring_entry = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
```

**Example Recurrence Patterns**:
```json
{
  "frequency": "weekly",
  "days": ["monday", "wednesday", "friday"],
  "end_date": "2026-12-31",
  "interval": 1
}
```

**Expected Benefits**:
- 95% reduction in manual entry for regular schedules
- "Set and forget" availability management
- Supports work hours, gym time, recurring meetings

**Acceptance Criteria**:
- [ ] User can create weekly recurring unavailability
- [ ] Recurring entries auto-generate for 90 days
- [ ] User can edit single occurrence
- [ ] User can edit entire series
- [ ] User can delete single occurrence
- [ ] User can delete entire series
- [ ] Calendar correctly displays recurring entries
- [ ] All tests passing with new feature

---

### Phase 3: Meeting Coordination (Q2 2026)

#### Feature 3: Meeting Proposals 🎯 **[PLANNED - FUTURE]**
**Priority**: MEDIUM (completes core workflow)
**Effort**: High (8-12 hours)
**Status**: 🔴 Planned

**Description**: Allow users to propose specific meeting times and coordinate acceptance.

**User Story**:
- User views group free times, clicks "Propose Meeting" on a slot
- Fills in: title, duration (30min/1hr/2hr), description
- System sends email notifications to all group members
- Members click Accept/Decline in email or web interface
- Once all accept, meeting auto-blocks time on personal calendars
- Meeting appears on group calendar as scheduled event

**Technical Requirements**:
- New model: `MeetingProposal` (group, proposed_by, datetime, duration, title, description, status)
- New model: `MeetingResponse` (proposal, user, response, responded_at)
- New views: Create proposal, view proposals, respond to proposal
- Email notifications using existing email backend
- Status tracking: pending → accepted → scheduled OR rejected
- Auto-create Unavailability entries when meeting scheduled
- Update group calendar to show scheduled meetings (not just free times)

**Database Schema**:
```python
class MeetingProposal(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    proposed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    datetime = models.DateTimeField()
    duration_minutes = models.IntegerField(choices=[(30, '30 min'), (60, '1 hour'), (120, '2 hours')])
    status = models.CharField(max_length=20, choices=[...])
    created_at = models.DateTimeField(auto_now_add=True)

class MeetingResponse(models.Model):
    proposal = models.ForeignKey(MeetingProposal, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    response = models.CharField(max_length=10, choices=[('accept', 'Accept'), ('decline', 'Decline')])
    responded_at = models.DateTimeField(auto_now_add=True)
```

**Expected Benefits**:
- Complete end-to-end scheduling workflow
- No external tools needed (Google Calendar, Doodle, etc.)
- Automatic calendar blocking
- Clear audit trail of who accepted/declined

**Acceptance Criteria**:
- [ ] User can propose meeting from free time slot
- [ ] Email notifications sent to group members
- [ ] Members can accept/decline via web or email
- [ ] Meeting auto-schedules when all accept
- [ ] Meeting auto-rejects if anyone declines
- [ ] Scheduled meetings block personal calendars
- [ ] Group calendar shows scheduled meetings
- [ ] All tests passing with new feature

---

## 🔮 Future Considerations (Backlog)

### Low Priority Enhancements

**Calendar Export (iCal)**
- Export personal unavailability to .ics file
- Import into Google Calendar, Outlook, Apple Calendar
- Effort: Low (2-3 hours)

**Time Zone Support**
- Display free times in different time zones
- Store user's preferred timezone in profile
- Effort: Low (2-3 hours)

**Group Dashboard View**
- Single page showing all groups and their next available slot
- Quick overview without clicking into each group
- Effort: Low (2-3 hours)

**Visual Calendar Grid**
- Traditional month/week view (like Google Calendar)
- JavaScript calendar library integration (FullCalendar.js)
- Effort: Medium (4-6 hours)

**Smart Meeting Suggestions**
- AI-powered optimal meeting time suggestions
- Score slots by availability, time zones, preferences
- Effort: Medium (4-6 hours)

**User Preferences**
- Preferred meeting times (mornings vs afternoons)
- Max meetings per day
- Buffer time between meetings
- Email notification settings
- Effort: Medium (4-6 hours)

**Statistics Dashboard**
- Hours marked unavailable this week
- Most common free time across groups
- Meeting acceptance rate
- Effort: Low (2-3 hours)

---

## 📊 Success Metrics

### Phase 1 Goals
- **Onboarding Time**: Reduce from 5 minutes to 30 seconds (join code feature)
- **User Retention**: 20% increase in weekly active users
- **Group Growth**: 50% increase in average group size

### Phase 2 Goals
- **Data Entry**: 90% reduction in manual calendar entries
- **User Satisfaction**: 4.5/5 stars on ease-of-use survey
- **Time Saved**: Average 10 minutes saved per user per week

### Phase 3 Goals
- **Meeting Coordination**: 100% of scheduling done in-app (no external tools)
- **Proposal Success Rate**: 80% of proposals result in scheduled meetings
- **User Engagement**: 3x increase in daily active users

---

## 🛠️ Development Process

### For Each Feature
1. **Design Phase**: Review requirements, create mockups if needed
2. **Database Migration**: Plan and implement schema changes
3. **Backend Development**: Models, views, forms, utilities
4. **Frontend Development**: Templates, JavaScript, CSS
5. **Testing**: Unit tests, integration tests, live testing
6. **Code Review**: Pylint, security scans, mutation testing
7. **Documentation**: Update CLAUDE.md, README.md, user guides
8. **Deployment**: Production deployment, smoke testing

### Quality Gates
- All tests passing (144+ tests)
- Pylint score 9.0+ or all issues fixed
- Mutation score 100%
- Code coverage 93%+ on critical modules
- Security scans: 0 vulnerabilities
- Live testing: All workflows verified

---

## 📅 Timeline

| Phase | Feature | Start Date | Target Completion | Status |
|-------|---------|------------|-------------------|--------|
| Phase 1 | Group Join Codes | Nov 23, 2025 | Nov 23, 2025 | 🟡 In Progress |
| Phase 2 | Recurring Unavailability | Nov 24, 2025 | Nov 30, 2025 | 🔴 Planned |
| Phase 3 | Meeting Proposals | Dec 1, 2025 | Dec 15, 2025 | 🔴 Planned |

---

## 🤝 Contribution Guidelines

When implementing roadmap features:
1. Create feature branch: `feature/join-codes` or `feature/recurring-unavailability`
2. Follow coding standards in STYLE_GUIDE.md
3. Run full test suite before committing (see CLAUDE.md testing workflow)
4. Update documentation (this file, README.md, CLAUDE.md)
5. Create pull request with description and testing evidence
6. All CI/CD checks must pass (GitHub Actions)

---

## 📝 Change Log

- **2025-11-23**: Roadmap created, Phase 1 (Join Codes) started
- **2025-11-02**: AI Code Review fixes completed (19/19 items)
- **2025-11-02**: Test suite reorganization complete
- **2025-11-02**: JavaScript extraction complete
- **2025-11-03**: Security vulnerabilities patched (CVE-2024-35195)
- **2025-11-03**: Live testing complete, all features verified

---

**Questions or Suggestions?** Open an issue on GitHub: https://github.com/manchesterjm/CS3300_Metting_Calendar/issues
