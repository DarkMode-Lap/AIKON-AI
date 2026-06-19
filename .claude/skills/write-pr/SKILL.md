---
name: write-pr
description: Write and open a GitHub Pull Request following the project PR template. No AI attribution or boilerplate.
allowed-tools: Bash(git log*), Bash(git diff*), Bash(git push*), Bash(git rev-parse*), Bash(git branch*), Bash(gh pr*), Bash(gh repo*), Bash(gh api*), Bash(gh auth status), Bash(gh issue*), Bash(gh label*), Read
---

## Step 1 — Collect Branch Info

```bash
git log develop...HEAD --oneline
git diff develop...HEAD --stat
git branch --show-current
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

## Step 4 — Find Related Issue

```bash
gh issue list --json number,title,body,labels --limit 50
```

이슈 매칭 순서:

1. **브랜치 이름 우선**: 브랜치 이름에서 숫자를 추출 (예: `feat/issue-3-...` → `#3`, `fix/7-...` → `#7`)
2. **시맨틱 매칭 fallback**: 브랜치 이름에 번호가 없으면 이슈 제목·본문과 커밋 메시지·변경 파일을 비교해 가장 관련성 높은 이슈 선택
3. **매칭 실패**: 확신할 수 없으면 `Close #` 그대로 두고 사용자에게 이슈 번호를 물어본다

찾은 이슈 번호로 PR 본문의 `- Close #` 라인을 `- Close #<number>` 로 채운다.

## Step 5 — Collect Repo Meta

```bash
gh repo view --json nameWithOwner -q .nameWithOwner
gh label list
gh api user --jq '.login'
```

## Step 6 — Create PR

```bash
git push -u origin HEAD
gh pr create --base develop \
  --title "<title>" \
  --body "$(cat /tmp/pr-body.md)" \
  --assignee "@me"
```
