# Async Conventions

## Rules

- All FastAPI route handlers must be `async def`
- Never call blocking I/O (network, file, DB) directly inside `async def` — wrap with `await asyncio.to_thread(func, args)`
- `chat_stream()` in `gemini.py` is an async generator — use `async for` at call sites
- Streaming endpoints: use `StreamingResponse` with `media_type="text/event-stream"`

## Known Issue

`app/services/gemini.py` calls `model.generate_content()` synchronously inside `async def`.
When fixing, wrap in `asyncio.to_thread()`:

```python
import asyncio
response = await asyncio.to_thread(model.generate_content, message)
```
