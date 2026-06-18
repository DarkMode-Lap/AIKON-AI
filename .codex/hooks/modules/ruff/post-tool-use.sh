#!/bin/bash
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')

if [[ "$TOOL_NAME" == "Edit" || "$TOOL_NAME" == "Write" || "$TOOL_NAME" == "write_file" ]]; then
    FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // empty')
    CWD=$(echo "$INPUT" | jq -r '.cwd // empty')

    if [[ "$FILE_PATH" == *.py ]]; then
        echo "[Hook] Running ruff format+check for $(basename "$FILE_PATH")" >&2
        cd "${CWD:-.}"
        if command -v uv > /dev/null 2>&1; then
            uv run ruff format "$FILE_PATH" 2>&1 && uv run ruff check --fix "$FILE_PATH" 2>&1
        else
            python -m ruff format "$FILE_PATH" 2>&1 && python -m ruff check --fix "$FILE_PATH" 2>&1
        fi
        if [[ $? -eq 0 ]]; then
            echo "[Hook] ruff OK" >&2
        else
            echo "[Hook] ruff failed" >&2
        fi
    fi
fi

exit 0
