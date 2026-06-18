---
name: git-commit
description: Split staged changes into logical commits following project conventions. Checks branch, warns if on main.
compatibility: Requires git
---

## Step 1 — Branch Check

```bash
git branch --show-current
```

If on `main` or `master`, warn and suggest creating a feature branch.

## Step 2 — Review Changes

```bash
git status
git diff
git diff --cached
```

## Step 3 — Categorize and Commit

Group related changes into logical units. For each unit:

1. `git add <specific files>`
2. `git commit -m "type :: 한국어 설명"`

Commit message rules:
- Format: `type :: 한국어 설명`
- Types: `add`, `update`, `fix`, `delete`, `docs`, `test`, `merge`, `init`, `chore`
- Description: Korean, no period
- **NEVER add** `Co-Authored-By` or any AI attribution line

## Step 4 — Verify

```bash
git log --oneline -n 5
```
