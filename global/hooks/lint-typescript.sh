#!/bin/bash
# afterFileEdit hook: auto-fix lint + format on TypeScript/JavaScript files
# Auto-detects: Biome (preferred) or ESLint
# Requires: biome or eslint in project devDependencies

filepath="${CURSOR_FILE_PATH:-${FILE_PATH:-$1}}"
[[ "$filepath" != *.ts && "$filepath" != *.tsx && "$filepath" != *.js && "$filepath" != *.jsx ]] && exit 0

# Find project root (nearest package.json)
dir=$(dirname "$filepath")
while [ "$dir" != "/" ] && [ ! -f "$dir/package.json" ]; do
    dir=$(dirname "$dir")
done
[ ! -f "$dir/package.json" ] && exit 0

cd "$dir"

# Prefer Biome, fallback to ESLint
if [ -f "biome.json" ] || [ -f "biome.jsonc" ]; then
    npx biome check --fix "$filepath" 2>/dev/null
elif [ -f "eslint.config.js" ] || [ -f "eslint.config.mjs" ] || [ -f ".eslintrc.json" ]; then
    npx eslint --fix "$filepath" 2>/dev/null
fi
