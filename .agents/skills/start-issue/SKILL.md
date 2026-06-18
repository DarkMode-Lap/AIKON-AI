---
name: start-issue
description: Draft a GitHub issue from the user's description, ask for approval, then create the issue, branch, and begin work.
compatibility: Requires git, gh (GitHub CLI)
---

## Step 1 — Repo & Branch Check

```bash
gh repo view --json nameWithOwner,defaultBranchRef -q '{repo: .nameWithOwner, default: .defaultBranchRef.name}'
git branch --show-current
gh label list
```

## Step 2 — Draft Issue

Based on the user's description, prepare:
- **제목**: 한국어, 50자 이내
- **본문**: `## 작업 내용` + `## 완료 조건` 섹션
- **라벨**: pick from `gh label list` output
- **브랜치명**: `feat/kebab-case-description`

## Step 3 — Ask for Approval

Show the draft and confirm with the user before creating anything.

## Step 4 — Create Issue (on approval)

```bash
gh issue create \
  --title "<제목>" \
  --body "<본문>" \
  --label "<라벨>"
ISSUE_NUMBER=$(gh issue list --limit 1 --state open --json number -q '.[0].number')
```

## Step 5 — Create Branch & Checkout

```bash
git checkout main && git pull
git checkout -b feat/issue-${ISSUE_NUMBER}-<kebab-description>
```

## Step 6 — Begin Work

Start implementing based on the completion conditions in the issue body.
Commit messages: `type :: 한국어 설명` (no AI attribution).
