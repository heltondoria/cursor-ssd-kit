#!/bin/bash
# afterFileEdit hook: auto-fix lint + format on Python files
# Requires: uv, ruff in project dev dependencies

filepath="${CURSOR_FILE_PATH:-${FILE_PATH:-$1}}"
[[ "$filepath" != *.py ]] && exit 0

# Find project root (nearest pyproject.toml)
dir=$(dirname "$filepath")
while [ "$dir" != "/" ] && [ ! -f "$dir/pyproject.toml" ]; do
    dir=$(dirname "$dir")
done
[ ! -f "$dir/pyproject.toml" ] && exit 0

cd "$dir"
uv run ruff check --fix "$filepath" 2>/dev/null
uv run ruff format "$filepath" 2>/dev/null
