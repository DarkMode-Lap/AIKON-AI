## Project Overview

AIKON-AI는 FastAPI + Google Gemini AI 기반 채팅 백엔드입니다.

## Commands

- **Run**: `uv run uvicorn main:app --reload`
- **Test**: `uv run pytest`
- **Lint**: `uv run ruff check .`
- **Format**: `uv run ruff format .`
- **Lint + fix**: `uv run ruff check --fix . && uv run ruff format .`
- **Install deps**: `uv sync --all-groups`
- **Add dep**: `uv add <package>`
- **Add dev dep**: `uv add --group dev <package>`

## Tech Stack

- **Runtime**: Python 3.11
- **Framework**: FastAPI
- **AI**: Google Gemini (`gemini-1.5-flash`) via `google-generativeai`
- **Config**: Pydantic Settings v2 (reads `.env`)
- **Testing**: pytest + pytest-asyncio (`asyncio_mode = "auto"`)
- **Lint/Format**: ruff
- **Package manager**: uv

## Project Structure

```
AIKON-AI/
├── main.py                    # FastAPI app, /health + mounts /api router
├── pyproject.toml             # uv project config + ruff config
├── .env.example               # GEMINI_API_KEY, OPENAI_API_KEY, DEBUG
├── app/
│   ├── api/v1/
│   │   └── chat.py            # POST /api/v1/chat, POST /api/v1/chat/stream
│   ├── core/config.py         # Pydantic Settings singleton
│   └── services/gemini.py     # chat(), chat_stream() — Gemini AI calls
└── tests/
    ├── conftest.py            # sets GEMINI_API_KEY=test-key
    └── test_health.py
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check — returns `{"status": "ok"}` |
| POST | `/api/v1/chat` | Sync chat — `{message}` → `{reply}` |
| POST | `/api/v1/chat/stream` | SSE streaming chat |

## Coding Rules

See `.claude/rules/` for details:
- `python-style.md` — type hints, Pydantic v2, import style
- `async-conventions.md` — async/await, known issue in `gemini.py`
- `commit-conventions.md` — commit format, branch naming, PR rules

## Skills

- `/git-commit` — split changes into logical commits
- `/write-pr` — create PR using project template
- `/start-issue` — create issue → branch → begin work
- `/resolve-reviews` — assess and respond to PR review comments

## Branch Strategy

Feature branches from `main`. Naming: `feat/`, `fix/`, `update/`, `add/`, `delete/`, `docs/`, `test/`, `init/` + `/kebab-case`.

## Context Compaction Priority

1. Project Overview + Commands
2. Coding Rules
3. Tech Stack
4. Reduce: Key Paths, API Endpoints
