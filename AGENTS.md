**한국어로 응답하고 작업해주세요 (Please respond and work in Korean).**

## Project Overview

AIKON-AI는 FastAPI + Google Gemini AI 기반 채팅 백엔드입니다.

## Tech Stack

- **Language**: Python 3.11
- **Framework**: FastAPI
- **AI Model**: Google Gemini (`gemini-1.5-flash`)
- **Config**: Pydantic Settings v2
- **Package manager**: uv
- **Testing**: pytest + pytest-asyncio
- **Lint/Format**: ruff

## Project Structure

```
AIKON-AI/
├── main.py                    # FastAPI app, /health endpoint, mounts /api
├── pyproject.toml             # uv + ruff config
├── .env.example               # GEMINI_API_KEY, OPENAI_API_KEY, DEBUG
├── app/
│   ├── api/v1/chat.py         # POST /api/v1/chat, POST /api/v1/chat/stream
│   ├── core/config.py         # Pydantic Settings singleton
│   └── services/gemini.py     # chat() and chat_stream()
└── tests/
    ├── conftest.py
    └── test_health.py
```

## Commands

- **Run**: `uv run uvicorn main:app --reload`
- **Test**: `uv run pytest`
- **Lint**: `uv run ruff check .`
- **Format**: `uv run ruff format .`
- **Install**: `uv sync --all-groups`

## Coding Conventions

### Python Style

- Python 3.11; type hints on all functions including return types
- Pydantic v2: `model_config = SettingsConfigDict(env_file=".env")` — never `class Config:`
- `BaseModel` for request/response; `BaseSettings` for app config
- Use `X | None` union syntax (Python 3.10+) over `Optional[X]`
- No `import *`; prefer explicit `from x import y`
- No excessive comments

### Async Rules

- All FastAPI route handlers: `async def`
- Blocking I/O inside async: wrap with `await asyncio.to_thread(func, args)`
- **Known issue**: `app/services/gemini.py` calls `model.generate_content()` synchronously — needs `asyncio.to_thread()` wrapping

### Commit Conventions

Format: `type :: 한국어 설명` (마침표 없음)

| Type | Meaning |
|------|---------|
| add | 새로운 코드나 파일 추가 |
| update | 기존 코드 수정 |
| fix | 버그 수정 |
| delete | 삭제 |
| docs | 문서 수정 |
| test | 테스트 추가/수정 |
| chore | 빌드 설정, 의존성 변경 |
| init | 프로젝트 초기화 |

**NEVER add** `Co-Authored-By: Codex` or any AI attribution line.

### Branch Naming

`prefix/kebab-case-description` — prefixes: `feat/`, `fix/`, `update/`, `add/`, `delete/`, `docs/`, `test/`, `init/`

### PR Rules

- Follow `.github/PULL_REQUEST_TEMPLATE.md` exactly (Korean)
- **NEVER add** AI attribution footer or any boilerplate beyond the template

## Notes

- `tests/conftest.py` sets `GEMINI_API_KEY=test-key` so tests run without a real key
- `.env` is gitignored; copy `.env.example` to `.env` and fill in real values
- CI runs `uv run pytest` on push/PR to `main`
