---
name: resolve-reviews
description: Collect PR review comments, critically assess each one against project conventions, auto-apply valid ones, post refutation replies for invalid ones, and prompt for partial ones.
compatibility: Requires git, gh (GitHub CLI), and jq
---

## Step 1 — Collect PR Data

```bash
bash scripts/get-pr-data.sh
```

Output files:
- `.pr-tmp/pr_comments.json` — inline review comments (id, path, line, body, user)
- `.pr-tmp/pr_changed_files.txt` — changed files
- `.pr-tmp/pr_commits.txt` — commits in this PR
- `.pr-tmp/pr_diff.txt` — full diff

```bash
gh repo view --json nameWithOwner -q .nameWithOwner
gh pr view --json number,baseRefName -q '{number: .number, base: .baseRefName}'
```

## Step 2 — Assess Each Comment

Cross-reference `CLAUDE.md`, `AGENTS.md`, and project conventions.

**Rule priority**: `CLAUDE.md` > `AGENTS.md` > language/framework best practices

### Verdicts

- **VALID**: reviewer is correct → attempt auto code fix
- **INVALID**: reviewer is wrong → skip, post refutation reply
- **PARTIAL**: ambiguous → confirm with user

## Step 3 — Act on Each Verdict

### VALID → Auto fix + commit

```bash
git add <file>
git commit -m "fix :: 리뷰 반영 — <변경 내용 한 줄 요약>"
git rev-parse --short=7 HEAD
```

### INVALID → Skip

Record refutation rationale.

### PARTIAL → Confirm

Ask user: `Accept? (y / n / s)`

## Step 4 — Print Report

```
| # | Reviewer | File | Verdict | Rationale | Action |
```

## Step 5 — Push

```bash
git push
```

## Step 6 — Post GitHub Replies

```bash
gh api "repos/<owner>/<repo>/pulls/<pr_number>/comments/<comment_id>/replies" \
  -f body="<reply_body>"
```

Reply templates (Korean):
- VALID success: `<abc1234> 에서 반영했습니다. (근거: <출처>)`
- INVALID: `해당 지적은 이 프로젝트의 컨벤션과 다릅니다. 근거: <출처>`
- PARTIAL accepted: `부분적으로 타당하다고 판단하여 <abc1234> 에서 반영했습니다.`

## Step 7 — Cleanup

```bash
rm -rf .pr-tmp
```
