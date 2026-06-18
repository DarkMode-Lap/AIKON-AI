# Python Style Rules

- Python version: 3.11 (CI installs 3.11)
- All function signatures must have type hints, including return types
- Pydantic v2: use `model_config = SettingsConfigDict(...)` — never the v1 `class Config:` inner class
- `BaseModel` for request/response schemas; `BaseSettings` for app config
- Use `X | None` union syntax (Python 3.10+) over `Optional[X]`
- No `import *` anywhere — use explicit `from x import y`
- Constants in SCREAMING_SNAKE_CASE at module top level
- No excessive comments — only where logic is non-obvious
