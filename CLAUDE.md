# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**cursor-ssd-kit** — Cursor IDE configuration kit implementing the Specification-Driven Development (SDD) pipeline. Adapted from claude-code-sdd-kit for Cursor 2.4+.

## Structure

```
cursor-ssd-kit/
├── README.md              # Documentation and installation guide
├── install.sh             # Installation script (copies to ~/.cursor/)
└── global/                # → ~/.cursor/
    ├── rules/             # 6 .mdc rule files (replaces CLAUDE.md global)
    ├── skills/            # 14 skills (SDD pipeline)
    ├── hooks/             # 4 shell scripts (lint, typecheck, block)
    ├── hooks.json         # Cursor hooks configuration
    ├── agents/            # 2 agents (convention-checker, security-bug-reviewer)
    ├── scripts/           # 1 script (sdd-metrics.py)
    └── templates/         # 7 golden config templates
```

## Key Conventions

- All paths reference `~/.cursor/` (not `~/.claude/`)
- Hook scripts use fallback chain: `${CURSOR_FILE_PATH:-${FILE_PATH:-$1}}`
- Rules use `.mdc` format with YAML frontmatter
- No `disable-model-invocation` in skill frontmatter (Cursor-incompatible)
- No `enabledPlugins` section (Cursor handles extensions separately)
- Hook timeouts in seconds (not milliseconds)
- Hook events: `afterFileEdit`/`preToolUse` (not `PostToolUse`/`PreToolUse`)

## Verification

```bash
# Check no remaining Claude Code references
grep -rn "~/.claude\|CLAUDE_FILE_PATH\|claude-code\|Claude Code" global/ \
  --include="*.md" --include="*.sh" --include="*.json" --include="*.mdc"
```
