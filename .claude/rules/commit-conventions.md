# Commit & PR Conventions

## Commit Message Format

`type :: 한국어 설명`

- Description: Korean, no period at end
- **NEVER add** `Co-Authored-By: Claude`, `Co-Authored-By: Codex`, or any AI attribution line

## Commit Types

| Type | Meaning |
|------|---------|
| add | 새로운 코드나 파일을 추가하였을 때 |
| update | 기존의 코드를 수정했을 때 |
| fix | 버그를 수정했을 때 |
| delete | 삭제한 사항이 있을 때 |
| docs | 문서를 수정 |
| test | 테스트 관련 사항을 추가/수정하였을 때 |
| merge | 브랜치를 병합하였을 때 |
| init | 프로젝트 초기화 시 |
| chore | 빌드 설정, 의존성 변경 등 기타 작업 |

## Examples

```
add :: Gemini 스트리밍 응답 엔드포인트 구현
fix :: 환경 변수 누락 시 서버 시작 오류 수정
update :: ruff 린트 훅 설정 추가
docs :: CLAUDE.md 초기 작성
chore :: pyproject.toml ruff 의존성 추가
```

## Branch Naming

Format: `prefix/kebab-case-description`
Allowed prefixes: `feat/`, `fix/`, `update/`, `add/`, `delete/`, `docs/`, `test/`, `init/`

## PR Rules

- PR body must follow `.github/PULL_REQUEST_TEMPLATE.md` exactly (Korean)
- **NEVER add**: "🤖 Generated with Claude Code", AI attribution footer, or any auto-generated text beyond the template
