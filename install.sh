#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/global"
TARGET_DIR="${HOME}/.cursor"

if [[ ! -d "${SOURCE_DIR}" ]]; then
  echo "ERROR: global/ directory not found at ${SOURCE_DIR}" >&2
  exit 1
fi

# Backup existing config
if [[ -d "${TARGET_DIR}" ]]; then
  BACKUP_DIR="${TARGET_DIR}.bak-$(date +%Y%m%d-%H%M%S)"
  cp -r "${TARGET_DIR}" "${BACKUP_DIR}"
  echo "Backup created: ${BACKUP_DIR}"
else
  BACKUP_DIR=""
  echo "No existing ~/.cursor/ found — skipping backup"
fi

# Ensure target directory exists
mkdir -p "${TARGET_DIR}"

# Copy top-level files
for file in hooks.json; do
  if [[ -f "${SOURCE_DIR}/${file}" ]]; then
    cp "${SOURCE_DIR}/${file}" "${TARGET_DIR}/${file}"
  fi
done

# Copy directories (merge, not replace)
for dir in rules skills hooks agents templates; do
  if [[ -d "${SOURCE_DIR}/${dir}" ]]; then
    mkdir -p "${TARGET_DIR}/${dir}"
    cp -r "${SOURCE_DIR}/${dir}/." "${TARGET_DIR}/${dir}/"
  fi
done

# Make hook scripts executable
if [[ -d "${TARGET_DIR}/hooks" ]]; then
  chmod +x "${TARGET_DIR}/hooks/"*.sh 2>/dev/null || true
fi

# Summary
echo ""
echo "=== SDD Kit installed (Cursor) ==="
if [[ -n "${BACKUP_DIR:-}" ]]; then
  echo "Backup:    ${BACKUP_DIR}"
fi
echo "Target:    ${TARGET_DIR}"

count_items() {
  local dir="$1" type="$2"
  if [[ -d "${dir}" ]]; then
    local count
    count=$(find "${dir}" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)
    if [[ "${count}" -eq 0 ]]; then
      count=$(find "${dir}" -mindepth 1 -maxdepth 1 -type f 2>/dev/null | wc -l)
    fi
    echo "${type}: ${count}"
  fi
}

count_items "${TARGET_DIR}/rules" "Rules"
count_items "${TARGET_DIR}/skills" "Skills"
count_items "${TARGET_DIR}/hooks" "Hooks"
count_items "${TARGET_DIR}/agents" "Agents"
count_items "${TARGET_DIR}/templates" "Templates"
