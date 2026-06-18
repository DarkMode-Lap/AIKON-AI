---
description: Collect PR review comments, critically assess each one against project conventions, auto-apply valid ones, post refutation replies for invalid ones, and prompt for partial ones.
allowed-tools: Bash(bash *), Bash(gh api*), Bash(gh pr*), Bash(gh repo*), Bash(git add*), Bash(git commit*), Bash(git log*), Bash(git push*), Bash(git rev-parse*), Bash(rm -rf .pr-tmp), Edit, Read
---

## Step 1 — Collect PR Data

```bash
bash .claude/skills/resolve-reviews/scripts/get-pr-data.sh
```

Output files:
- `.pr-tmp/pr_comments.json` — inline review comments (id, path, line, body, user)
- `.pr-tmp/pr_changed_files.txt` — changed files
- `.pr-tmp/pr_commits.txt` — commits in this PR
- `.pr-tmp/pr_diff.txt` — full diff

Also fetch repo and PR metadata:

```bash
gh repo view --json nameWithOwner -q .nameWithOwner
gh pr view --json number,baseRefName -q '{number: .number, base: .baseRefName}'
```

## Step 2 — Load Rules and Assess Each Comment

Before assessing any comment, discover and read all project convention files:

```bash
find .claude/rules -name "*.md" 2>/dev/null
```

Read each returned file in full.

**Rule priority**: `CLAUDE.md` > `.claude/rules/**` > `AGENTS.md`

For each comment in `pr_comments.json`, apply the following **layered judgment criteria**:

### Judgment criteria (priority order)

1. **Project conventions** (primary): apply rules discovered above
2. **Language/framework best practices** (secondary): Python official guide, FastAPI recommendations
   - Apply only when no matching project rule exists

### Verdicts

- **VALID**: reviewer is correct → attempt auto code fix
- **INVALID**: reviewer is wrong with a clear refutation → skip, post refutation reply
- **PARTIAL**: intent is correct but application method or scope is ambiguous → confirm with AskUserQuestion

Always cite a specific source in the rationale (e.g. `.claude/rules/python-style.md §Type Hints`, `FastAPI: prefer async def`).

## Step 3 — Act on Each Verdict

### VALID → Auto fix

1. Read the target file with the Read tool
2. Apply the reviewer's concern with the Edit tool
3. Commit the changes:
   ```bash
   git add <file>
   git commit -m "fix :: 리뷰 반영 — <변경 내용 한 줄 요약>"
   ```
4. Record the short commit hash:
   ```bash
   git rev-parse --short=7 HEAD
   ```

On failure: record the reason and fall back to PARTIAL.

### INVALID → Skip

Do not modify any code. Record the refutation rationale for Step 6.

### PARTIAL → Confirm with AskUserQuestion

Ask:
```
⚠️ PARTIAL: [file:line] (reviewer)
Review: "..."
Rationale: ...
Accept? (y / n / s = skip for now)
```

- `y`: treat as VALID, attempt code fix
- `n`: treat as INVALID, skip
- `s` / other: record as PENDING

## Step 4 — Print Report

```
## resolve-reviews Results

| # | Reviewer | File | Verdict | Rationale | Action |
|---|----------|------|---------|-----------|--------|
| 1 | alice | foo.py:12 | ✅ VALID | .claude/rules/python-style.md §Type Hints | Auto-fixed (abc1234) |
| 2 | bob | bar.py:34 | ❌ INVALID | .claude/rules/async-conventions.md | Skipped |
| 3 | alice | baz.py:56 | ⚠️ PARTIAL | - | PENDING |
```

## Step 5 — Push Commits

If any VALID fixes were committed in Step 3, push before posting replies:

```bash
git push
```

## Step 6 — Post GitHub Replies

Post an inline reply for each comment:

```bash
gh api "repos/<owner>/<repo>/pulls/<pr_number>/comments/<comment_id>/replies" \
  -f body="<reply_body>"
```

For reply body templates, read `.claude/skills/resolve-reviews/references/reply-formats.md`.

## Step 7 — Cleanup

```bash
rm -rf .pr-tmp
```
