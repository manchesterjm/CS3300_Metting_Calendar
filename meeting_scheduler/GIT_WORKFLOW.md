# Git Workflow & PR Process

This document describes the proper workflow for making changes to the Meeting Scheduler project using feature branches and pull requests.

## Branch Structure

```
main (production)
  ↑
  │ (PR after CI passes)
  │
develop (staging)
  ↑
  │ (PR for features)
  │
feature/* (feature branches)
```

### Branch Descriptions

- **`main`** - Production-ready code. Protected branch. Only merge via PR after CI passes.
- **`develop`** - Development branch. Base for all feature branches.
- **`feature/*`** - Individual feature branches (e.g., `feature/add-notifications`)

## Workflow for Making Changes

### Step 1: Create a Feature Branch

Always branch off from `develop`:

```bash
# Make sure you're on develop and up to date
git checkout develop
git pull origin develop

# Create a new feature branch
git checkout -b feature/your-feature-name

# Example:
git checkout -b feature/add-email-notifications
```

**Branch Naming Conventions:**
- `feature/` - New features (e.g., `feature/add-notifications`)
- `fix/` - Bug fixes (e.g., `fix/login-error`)
- `refactor/` - Code refactoring (e.g., `refactor/database-queries`)
- `docs/` - Documentation changes (e.g., `docs/update-readme`)
- `test/` - Test additions/changes (e.g., `test/add-integration-tests`)

### Step 2: Make Your Changes

Work on your feature:

```bash
# Make changes to files
# Edit code, add features, fix bugs, etc.

# Check what changed
git status
git diff

# Stage changes
git add <file1> <file2>
# Or add all changes
git add .

# Commit with descriptive message
git commit -m "Add email notification system

- Implement SMTP email backend
- Create notification templates
- Add user notification preferences
- Update settings for email configuration"
```

**Commit Message Best Practices:**
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed description of what and why
- Reference issue numbers if applicable

### Step 3: Push Feature Branch to GitHub

```bash
# Push your feature branch
git push -u origin feature/your-feature-name
```

### Step 4: Create Pull Request on GitHub

1. **Go to your repository**: https://github.com/manchesterjm/CS3300_Metting_Calendar

2. **GitHub will show a banner**: "Your recently pushed branches: feature/your-feature-name"
   - Click **"Compare & pull request"**

3. **Or manually create PR**:
   - Click "Pull requests" tab
   - Click "New pull request"
   - Base: `develop` (or `main` for production)
   - Compare: `feature/your-feature-name`
   - Click "Create pull request"

4. **Fill out PR details**:
   ```markdown
   ## Description
   Brief description of what this PR does.

   ## Changes
   - Feature 1
   - Feature 2
   - Bug fix 3

   ## Testing
   - [ ] All tests pass locally
   - [ ] Added new tests for new features
   - [ ] Tested manually in browser

   ## Screenshots (if applicable)
   [Add screenshots here]
   ```

5. **Click "Create pull request"**

### Step 5: Wait for CI/CD Pipeline

**Automatic Checks Will Run:**

✅ **1. CI - Comprehensive Test Suite** (`ci.yml`)
- Pylint (code quality)
- Unit tests (62 tests)
- Fuzz tests (16 tests)
- All tests (78 tests)
- Mutation tests (100% score)
- Coverage (74%+ required)
- Security scans

✅ **2. AI Code Review** (`ai-code-review.yml`)
- OpenAI GPT-4o-mini review
- Posts intelligent comments on your PR
- ⚠️ Requires `OPENAI_API_KEY` secret (see GITHUB_SECRETS_SETUP.md)

✅ **3. Coverage Report** (`coverage.yml`)
- Posts coverage results as PR comment
- Shows module-level coverage breakdown

**Check Status:**
- Green ✅ - All checks passed, ready to merge
- Red ❌ - Checks failed, needs fixes
- Yellow ⏳ - Checks running, wait

### Step 6: Review & Address Feedback

**If CI Fails:**
1. Click on the failed check to see details
2. Fix the issues locally
3. Commit and push the fixes:
   ```bash
   # Fix the code
   git add .
   git commit -m "Fix: Resolve pylint errors"
   git push
   ```
4. CI will automatically re-run

**If AI Code Review Suggests Changes:**
- Review the AI's suggestions
- Implement valuable feedback
- Push changes to the same branch

**Code Review Process:**
- Team members can review your code
- Address comments and suggestions
- Mark conversations as resolved

### Step 7: Merge Pull Request

**Once All Checks Pass:**

1. ✅ All CI checks are green
2. ✅ Code review approved (if required)
3. ✅ No merge conflicts

**Merge Options:**

**Option A: Squash and Merge (Recommended)**
- Combines all commits into one
- Keeps history clean
- Use for feature branches with many small commits

**Option B: Create a Merge Commit**
- Preserves all individual commits
- Use for important features with meaningful commit history

**Option C: Rebase and Merge**
- Linear history
- Use if you want clean, linear history

**Click "Squash and merge" or "Merge pull request"**

### Step 8: Clean Up

**After Merging:**

```bash
# Switch back to develop
git checkout develop

# Pull latest changes (includes your merged PR)
git pull origin develop

# Delete local feature branch (optional)
git branch -d feature/your-feature-name

# Delete remote feature branch (GitHub usually does this automatically)
git push origin --delete feature/your-feature-name
```

## Quick Reference

### Daily Workflow

```bash
# Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/my-feature

# Work on feature
# ... make changes ...
git add .
git commit -m "Add feature X"

# Push and create PR
git push -u origin feature/my-feature
# Then create PR on GitHub

# After PR merged
git checkout develop
git pull origin develop
git branch -d feature/my-feature
```

### Example: Complete Feature Development

```bash
# 1. Create feature branch
git checkout develop
git pull origin develop
git checkout -b feature/add-notifications

# 2. Implement feature
# ... write code ...
git add calendar_app/notifications.py
git add calendar_app/templates/notifications/
git commit -m "Add email notification system

- Implement notification model
- Create email templates
- Add notification preferences to user settings"

# 3. Run tests locally
cd meeting_scheduler
python manage.py test calendar_app

# 4. Push to GitHub
git push -u origin feature/add-notifications

# 5. Create PR on GitHub
# ... create PR in browser ...

# 6. Wait for CI checks
# ... CI runs automatically ...

# 7. Address feedback (if any)
# ... make changes ...
git add .
git commit -m "Fix: Address code review feedback"
git push

# 8. Merge PR (in browser)
# ... click "Squash and merge" ...

# 9. Clean up
git checkout develop
git pull origin develop
git branch -d feature/add-notifications
```

## CI/CD Pipeline Details

### What Runs on Pull Requests

1. **All Python versions** (3.11, 3.12, 3.13)
2. **Code quality checks** (Pylint)
3. **All test suites** (unit, fuzz, mutation)
4. **Security scans** (Bandit, pip-audit)
5. **AI code review** (if OPENAI_API_KEY configured)
6. **Coverage report** (posted as comment)

### When CI Runs

- ✅ On every push to a PR branch
- ✅ On every new PR
- ✅ When PR is updated
- ✅ Can be manually re-run

### How to Re-run Failed CI

1. Go to PR page
2. Scroll to checks section
3. Click "Re-run failed jobs" or "Re-run all jobs"

## Protected Branches

### Main Branch Protection (Recommended Setup)

**Settings → Branches → Add rule for `main`:**

- ✅ Require pull request before merging
- ✅ Require status checks to pass before merging
  - Select: `test (3.13)` (or all Python versions)
  - Select: `test-summary`
- ✅ Require conversation resolution before merging
- ✅ Do not allow bypassing the above settings

**This ensures:**
- No direct pushes to `main`
- All code goes through PR review
- CI must pass before merging

## Troubleshooting

### Merge Conflicts

If your PR has conflicts with `develop`:

```bash
# Update your feature branch
git checkout feature/your-feature
git pull origin develop
# Resolve conflicts in your editor
git add .
git commit -m "Merge develop and resolve conflicts"
git push
```

### Failed CI Checks

1. **Click on the failed check** to see details
2. **Common failures**:
   - Pylint errors → Fix code style issues
   - Test failures → Fix broken tests
   - Coverage too low → Add more tests
   - Security issues → Fix vulnerabilities

3. **Fix locally**, then:
   ```bash
   git add .
   git commit -m "Fix: Resolve CI failures"
   git push
   ```

### Outdated Branch

If your branch is behind `develop`:

```bash
git checkout feature/your-feature
git pull origin develop
git push
```

## Best Practices

### ✅ Do's

- ✅ Create small, focused PRs (easier to review)
- ✅ Write descriptive commit messages
- ✅ Run tests locally before pushing
- ✅ Keep feature branches up to date with `develop`
- ✅ Delete branches after merging
- ✅ Review your own PR before requesting review
- ✅ Respond to code review feedback promptly

### ❌ Don'ts

- ❌ Don't push directly to `main`
- ❌ Don't merge PRs with failing CI
- ❌ Don't create massive PRs (thousands of lines)
- ❌ Don't force push to shared branches
- ❌ Don't commit secrets or API keys
- ❌ Don't skip code review process

## Summary

**Standard Workflow:**
1. Branch from `develop` → `feature/my-feature`
2. Make changes and commit
3. Push to GitHub
4. Create Pull Request
5. Wait for CI to pass (all green ✅)
6. Get code review (optional but recommended)
7. Merge PR (squash and merge)
8. Delete feature branch
9. Pull latest `develop`

**Every change goes through CI/CD before reaching `main`!**

This ensures high code quality and prevents bugs from reaching production.

## Additional Resources

- **GitHub Docs**: https://docs.github.com/en/pull-requests
- **Git Branching**: https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows
- **CI/CD Guide**: See `DEPLOYMENT.md`
- **GitHub Secrets Setup**: See `GITHUB_SECRETS_SETUP.md`
