# GitHub Secrets Setup Guide

This guide will help you set up the required secrets for your CI/CD workflows, specifically the OpenAI API key for AI code reviews.

## Overview

Your CI/CD pipeline now includes:
1. **CI Pipeline** (`.github/workflows/ci.yml`) - Comprehensive testing
2. **AI Code Review** (`.github/workflows/ai-code-review.yml`) - OpenAI-powered code review on PRs
3. **Coverage Report** (`.github/workflows/coverage.yml`) - Coverage reports as PR comments

## Required Secrets

### 1. OPENAI_API_KEY (Required for AI Code Review)

The AI code review workflow uses OpenAI's GPT-4 to provide intelligent code reviews on pull requests.

#### How to Get Your OpenAI API Key:

**Step 1: Log into OpenAI Platform**
1. Go to https://platform.openai.com
2. Sign in with your OpenAI account (you mentioned you have a paid account)

**Step 2: Navigate to API Keys**
1. Click on your profile icon (top right)
2. Select **"API keys"** from the dropdown menu
   - Or directly visit: https://platform.openai.com/api-keys

**Step 3: Create a New API Key**
1. Click the **"+ Create new secret key"** button
2. Give it a descriptive name (e.g., "GitHub Actions - Meeting Scheduler")
3. (Optional) Set usage limits to control spending
4. Click **"Create secret key"**

**Step 4: Copy Your API Key**
⚠️ **IMPORTANT**: Copy the key immediately! You won't be able to see it again.
- Format: `sk-proj-...` or `sk-...`
- Store it securely (you'll add it to GitHub in the next section)

#### API Key Best Practices:
- ✅ Use project-specific keys (not your primary account key)
- ✅ Set usage limits to prevent unexpected charges
- ✅ Rotate keys periodically for security
- ✅ Never commit keys to your repository
- ✅ Monitor usage on OpenAI dashboard: https://platform.openai.com/usage

#### OpenAI Pricing (as of 2024):
- **GPT-4o-mini** (default in workflow): ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- **GPT-4o**: ~$2.50 per 1M input tokens, ~$10 per 1M output tokens
- Typical code review: $0.01 - $0.05 per PR
- Estimated monthly cost: $1 - $10 (depending on PR frequency)

### 2. GITHUB_TOKEN (Automatically Provided)

The `GITHUB_TOKEN` is automatically provided by GitHub Actions. You don't need to create this - it's already available in all workflows.

### 3. OPENAI_MODEL (Optional)

If you want to use a specific OpenAI model, you can set this secret. Otherwise, it defaults to `gpt-4o-mini`.

**Available Models:**
- `gpt-4o-mini` (default) - Fast, cheap, good quality
- `gpt-4o` - Highest quality, more expensive
- `gpt-4-turbo` - Good balance of speed and quality
- `gpt-3.5-turbo` - Cheapest, fastest, lower quality

## Adding Secrets to GitHub

### Step-by-Step Guide:

**Step 1: Go to Your GitHub Repository**
1. Navigate to: https://github.com/manchesterjm/CS3300_Metting_Calendar
2. Click on **"Settings"** (tab at the top)

**Step 2: Navigate to Secrets**
1. In the left sidebar, click **"Secrets and variables"**
2. Click **"Actions"**

**Step 3: Add OPENAI_API_KEY**
1. Click **"New repository secret"** (green button)
2. **Name**: `OPENAI_API_KEY`
3. **Secret**: Paste your OpenAI API key (e.g., `sk-proj-...`)
4. Click **"Add secret"**

**Step 4: (Optional) Add OPENAI_MODEL**
1. Click **"New repository secret"** again
2. **Name**: `OPENAI_MODEL`
3. **Secret**: Enter model name (e.g., `gpt-4o-mini`)
4. Click **"Add secret"**

### Verify Secrets Are Set:
After adding secrets, you should see them listed under **Repository secrets**:
- ✅ `OPENAI_API_KEY` (will show as `***`)
- ✅ `OPENAI_MODEL` (optional, will show as `***`)

## Workflow Behavior

### AI Code Review Workflow

**When it runs:**
- On every pull request that modifies `.py`, `.md`, `.html`, `.js`, or `.ts` files
- Manually triggered from Actions tab

**What it does:**
1. Checks out your code
2. Shows changed files in the run log
3. Sends code changes to OpenAI GPT-4o-mini
4. Posts review comments directly on your PR

**Review Focus:**
- Django best practices
- Potential bugs/issues
- Security concerns
- Performance considerations
- Suggestions for improvement

**Example Comment:**
```markdown
🤖 AI Code Review

**File**: calendar_app/models.py:25-30
**Issue**: Security Concern

The user input is not sanitized before being stored in the database.
Consider using Django's built-in validators or clean methods.

**Suggestion**:
```python
def clean(self):
    self.name = bleach.clean(self.name)
```
```

### Coverage Workflow

**When it runs:**
- On every push to main/master/develop
- On every pull request to main/master/develop

**What it does:**
1. Runs Django tests with coverage tracking
2. Generates coverage report
3. Posts coverage results as a PR comment (for PRs only)
4. Uploads coverage artifacts

**Example PR Comment:**
```markdown
📊 Test Coverage Report

Overall Coverage: 93.5%

Critical Modules Coverage:
| Module     | Coverage |
|------------|----------|
| models.py  | 100%     |
| forms.py   | 99%      |
| views.py   | 94%      |

Total Tests Run: 62 ✅
```

## Troubleshooting

### Issue: AI Code Review Not Running

**Check:**
1. ✅ OPENAI_API_KEY is set in GitHub Secrets
2. ✅ PR modifies Python/HTML/JS/TS/MD files
3. ✅ Workflow file is in `.github/workflows/ai-code-review.yml`

**View Logs:**
1. Go to your PR
2. Scroll to bottom → "Checks" section
3. Click on "AI Code Review" → "Details"

### Issue: "Invalid API Key" Error

**Solutions:**
1. Verify your API key is correct on OpenAI platform
2. Regenerate the API key on OpenAI platform
3. Update the `OPENAI_API_KEY` secret in GitHub
4. Make sure you copied the full key (starts with `sk-proj-` or `sk-`)

### Issue: "Rate Limit Exceeded"

**Solutions:**
1. Check your OpenAI usage: https://platform.openai.com/usage
2. Increase usage limits on OpenAI platform
3. Wait a few minutes and re-run the workflow
4. Consider switching to a lower rate model (gpt-4o-mini)

### Issue: Coverage Workflow Fails

**Check:**
1. ✅ `requirements.txt` and `requirements-dev.txt` are present
2. ✅ Django tests are in `calendar_app/tests.py`
3. ✅ All dependencies install successfully

**View Logs:**
- Actions tab → "Django Tests with Coverage" → Click on failed run

## Disabling Workflows (If Needed)

### Temporarily Disable AI Code Review:
1. Go to `.github/workflows/ai-code-review.yml`
2. Comment out the entire file with `#` at the start of each line
3. Or rename the file to `ai-code-review.yml.disabled`

### Temporarily Disable Coverage Report:
1. Go to `.github/workflows/coverage.yml`
2. Comment out or rename similarly

## Cost Management

### Monitor OpenAI Usage:
1. Visit: https://platform.openai.com/usage
2. Set up usage alerts: https://platform.openai.com/settings/organization/billing/limits

### Reduce Costs:
1. **Use gpt-4o-mini** (default) instead of gpt-4o
2. **Limit max_completion_tokens** in workflow (currently 8000)
3. **Reduce temperature** (currently 0.7, lower = cheaper)
4. **Only run on specific file types** (already configured)
5. **Set monthly spending limits** on OpenAI platform

### Expected Monthly Costs:
- **Low activity** (5 PRs/month): ~$0.50 - $2
- **Medium activity** (20 PRs/month): ~$2 - $8
- **High activity** (50+ PRs/month): ~$5 - $20

## Testing Your Setup

### Test AI Code Review:
1. Create a new branch: `git checkout -b test-ai-review`
2. Modify a Python file: `echo "# test" >> calendar_app/models.py`
3. Commit and push: `git add . && git commit -m "Test" && git push`
4. Create a PR on GitHub
5. Wait 1-2 minutes for AI review to appear

### Test Coverage Report:
1. Same steps as above
2. Check PR comments for coverage report
3. Look for "📊 Test Coverage Report"

## Security Notes

### Secrets Security:
- ✅ GitHub encrypts all secrets
- ✅ Secrets are only exposed to workflows
- ✅ Secret values never appear in logs (shown as `***`)
- ✅ Only repository admins can add/edit secrets

### API Key Security:
- ✅ Never commit API keys to your repository
- ✅ Rotate keys if exposed
- ✅ Use project-specific keys (not account master key)
- ✅ Set usage limits to prevent abuse

## Additional Resources

- **OpenAI Platform**: https://platform.openai.com
- **OpenAI Pricing**: https://openai.com/pricing
- **GitHub Secrets Documentation**: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **GitHub Actions Documentation**: https://docs.github.com/en/actions
- **ChatGPT-CodeReview Action**: https://github.com/anc95/ChatGPT-CodeReview

## Support

If you encounter issues:
1. Check workflow logs in GitHub Actions
2. Verify secrets are set correctly
3. Check OpenAI platform for API issues
4. Review this guide for troubleshooting steps
