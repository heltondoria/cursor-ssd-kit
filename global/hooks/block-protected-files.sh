#!/bin/bash
# preToolUse hook: block editing of lock files and .env files
# Prevents accidental modification of generated/sensitive files

filepath="${CURSOR_FILE_PATH:-${FILE_PATH:-$1}}"

if echo "$filepath" | grep -qE '(\.(env|lock)$|uv\.lock|pnpm-lock\.yaml|package-lock\.json|yarn\.lock)$'; then
    echo "BLOCKED: Do not edit lock files or .env files directly." >&2
    exit 2
fi
