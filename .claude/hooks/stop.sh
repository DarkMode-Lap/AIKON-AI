#!/bin/bash
cd "${CLAUDE_PROJECT_DIR:-$PWD}" 2>/dev/null || exit 0
[[ ! -f "pyproject.toml" ]] && exit 0

echo "" >&2
echo "=== [AIKON-AI] Session End — Test Summary ===" >&2
uv run pytest tests/ -q --tb=no 2>&1 | tail -10 >&2
echo "=============================================" >&2

exit 0
