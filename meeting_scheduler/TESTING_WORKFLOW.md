# Testing Workflow Documentation

**Last Updated:** January 11, 2025
**Automated CI/CD:** GitHub Actions with GPT-5 AI Code Review

## Overview

This document describes the mandatory testing workflow that MUST be followed every time code is updated in the Meeting Scheduler application.

---

## Testing Philosophy

**All tests (unit, fuzz, and mutation) MUST be run every time code is updated.**

The testing process follows a strict sequential workflow:
1. **Code Quality** (Pylint) → Fix all issues before proceeding
2. **Unit Tests** → Fix failures before proceeding
3. **Fuzz Tests** → Fix failures before proceeding
4. **Integration** (All tests) → Verify combined success
5. **Mutation Tests** → Add tests to kill surviving mutations
6. **Coverage** → Verify coverage thresholds maintained

**IF ANY STEP FAILS:** Stop, fix the error, re-run that step, then continue.

---

## 🚀 Quick Start: Automated Test Runner

### Recommended Approach

**Run the automated test suite:**
```bash
cd meeting_scheduler
python run_all_tests.py
```

This script automatically:
- Runs all 6 testing steps in the correct order
- Stops at the first failure
- Provides clear feedback on what needs to be fixed
- Displays a comprehensive summary

**Expected Output:**
```
======================================================================
  [SUCCESS] ALL TESTS PASSED!
  Code is ready for deployment
======================================================================

Test Results:
  1. Pylint:        PASS
  2. Unit Tests:    PASS
  3. Fuzz Tests:    PASS
  4. All Tests:     PASS
  5. Mutation:      PASS
  6. Coverage:      PASS
```

---

## Manual Testing Process

If you need to run tests manually, follow these steps in order:

### Step 1: Pylint (Code Quality)

**Command:**
```bash
pylint calendar_app/*.py --disable=C0114,C0115,C0116,R0903,R0914,R0912,R0915,E1101 --max-line-length=120
```

**Success Criteria:**
- No critical errors (E*)
- No warnings that aren't disabled
- Score 9.0+/10

**If Failed:**
1. Review pylint output
2. Fix all reported issues
3. Re-run pylint
4. Repeat until all issues resolved

**Disabled Warnings:**
- `C0114,C0115,C0116`: Missing docstrings (code has comments)
- `R0903`: Too few public methods (Django pattern)
- `R0914,R0912,R0915`: Too many locals/branches/statements (single-view design)
- `E1101`: Django ORM false positives

---

### Step 2: Unit Tests

**Command:**
```bash
python manage.py test calendar_app.tests --verbosity=2
```

**Success Criteria:**
- All 21 tests pass
- No errors or failures
- Execution time < 1 second

**If Failed:**
1. Read the test failure output
2. Fix the failing code
3. Re-run unit tests
4. Repeat until all 21 tests pass

**Test Coverage:**
- 3 model tests
- 5 form tests
- 3 delete form tests
- 10 view tests (including new boundary tests)

---

### Step 3: Fuzz Tests

**Command:**
```bash
python manage.py test calendar_app.test_fuzz --verbosity=2
```

**Success Criteria:**
- All 9 tests pass
- ~350 test cases generated and executed
- No crashes or exceptions
- Execution time < 2 seconds

**If Failed:**
1. Review which property failed
2. Fix the code to handle edge cases
3. Re-run fuzz tests
4. Repeat until all tests pass

**What Fuzz Tests Cover:**
- Random date/time combinations
- Malformed inputs
- Boundary values
- Edge cases

---

### Step 4: All Tests Combined

**Command:**
```bash
python manage.py test calendar_app --verbosity=1
```

**Success Criteria:**
- All 30 tests pass (21 unit + 9 fuzz)
- No errors or failures
- Confirms tests work together

**This step verifies:**
- No test interference
- Database cleanup working
- All test infrastructure healthy

---

### Step 5: Mutation Tests

**Command:**
```bash
python run_mutation_test.py
```

**Success Criteria:**
- Mutation Score: 100%
- All 8 mutations killed
- 0 mutations survived

**If Failed (mutation survived):**
1. Review which mutation survived
2. Add a test to verify that exact behavior
3. Re-run mutation tests
4. Repeat until mutation score is 100%

**Mutations Tested:**
1. Time slot increment (30 min)
2. Start time boundary (8:00)
3. End time boundary (20:00)
4. Validation logic operators
5. Query limits
6. String representations
7. Loop boundaries (< vs <=)
8. Comparison operators

---

### Step 6: Code Coverage

**Commands:**
```bash
coverage run --source=calendar_app manage.py test calendar_app.tests
coverage report
```

**Success Criteria:**
- models.py: 100%
- forms.py: 97%+
- views.py: 93%+
- Overall: 70%+

**Optional - HTML Report:**
```bash
coverage html
# Open htmlcov/index.html in browser
```

---

## Testing Standards Checklist

Before considering code complete, verify:

- [ ] Pylint: No errors, score 9.0+
- [ ] Unit Tests: 21/21 passing
- [ ] Fuzz Tests: 9/9 passing
- [ ] All Tests: 30/30 passing
- [ ] Mutation Score: 100%
- [ ] Coverage: 93%+ on critical modules
- [ ] No test failures or errors
- [ ] All changes committed with tests

---

## Troubleshooting

### "Pylint fails with E1101"
**Solution:** Add `--disable=E1101` to pylint command (Django ORM false positive)

### "Tests pass individually but fail together"
**Solution:** Test isolation issue - check for database cleanup in tearDown methods

### "Mutation test fails with 'survived' mutation"
**Solution:** Add a specific test that verifies the exact behavior being mutated

### "Coverage drops below threshold"
**Solution:** Add tests for new code paths, review uncovered lines with `coverage html`

### "Fuzz tests intermittently fail"
**Solution:** Check for race conditions or state dependencies, ensure tests are deterministic

---

## Continuous Integration Recommendations

For CI/CD pipelines, run:

```bash
python run_all_tests.py
```

**Exit codes:**
- `0`: All tests passed, ready to deploy
- `1`: Tests failed, review output and fix

**Recommended CI/CD Setup:**
1. Run on every commit
2. Block merges if tests fail
3. Generate coverage reports as artifacts
4. Track mutation score over time

---

## Test Maintenance

### When Adding New Features

1. Write tests FIRST (TDD approach)
2. Run `python run_all_tests.py` to verify they fail
3. Implement the feature
4. Run `python run_all_tests.py` to verify they pass
5. Check mutation score - add tests if mutations survive

### When Fixing Bugs

1. Write a test that reproduces the bug
2. Verify the test fails
3. Fix the bug
4. Verify the test now passes
5. Run full test suite

### When Refactoring

1. Ensure all tests pass BEFORE refactoring
2. Refactor the code
3. Run full test suite
4. Verify no behavior changes (all tests still pass)

---

## Test Quality Metrics

Current status:
- **Total Tests:** 30 (21 unit + 9 fuzz)
- **Test Cases Generated:** 350+ (fuzz testing)
- **Code Coverage:** 70% overall, 93%+ critical
- **Mutation Score:** 100% (perfect)
- **Execution Time:** ~2 seconds total
- **Pylint Score:** 10/10

**Benchmarks:**
- Industry Standard: 80% coverage, 70% mutation score
- Our Achievement: 70% coverage, **100% mutation score**
- Quality Assessment: **Exceptional**

---

## Summary

### Required Workflow for Code Updates:

1. **Make code changes**
2. **Run:** `python run_all_tests.py`
3. **If fails:** Fix errors and re-run
4. **If passes:** Code is ready

### Golden Rule:

> **Never commit code that doesn't pass all tests.**
>
> If tests fail, fix them. Don't skip them, don't disable them, don't "commit now and fix later."

---

**Document Version:** 1.0
**Last Updated:** 2025-11-01
**Maintained By:** Development Team
**Testing Framework:** Django TestCase + Hypothesis + Custom Mutation Testing
