---
name: write-pr
description: Write and open a GitHub Pull Request following the project PR template. No AI attribution or boilerplate.
allowed-tools: Bash(git log*), Bash(git diff*), Bash(git push*), Bash(git rev-parse*), Bash(gh pr*), Bash(gh repo*), Bash(gh api*), Bash(gh auth status), Read
---

## Step 1 — Collect Branch Info

```bash
git log main...HEAD --oneline
git diff main...HEAD --stat
```

## Step 2 — Read Changed Files

Read key changed files to understand what was implemented.

## Step 3 — Write PR

### Title

짧고 명확한 한국어 설명 — `type ::` 접두사 없이 작성.
예시: `Gemini 스트리밍 응답 비동기 처리 개선`

### Body

Follow `.github/PULL_REQUEST_TEMPLATE.md` exactly (Korean).

**NEVER add**:
- "🤖 Generated with Claude Code"
- "Co-authored-by: Claude" or any AI attribution
- Any footer or boilerplate beyond the template sections

## Step 4 — Collect Repo Meta

```bash
gh repo view --json nameWithOwner -q .nameWithOwner
gh label list
gh api user --jq '.login'
```

## Step 5 — Create PR

```bash
git push -u origin HEAD
gh pr create --base main \
  --title "<title>" \
  --body "$(cat /tmp/pr-body.md)" \
  --assignee "@me"
```
