---
name: adopt
description: Migrate an existing project to the unified tooling standards (hooks, conventions, quality gates, CI)
argument-hint: [--dry-run] (optional: preview changes without applying)
---

# Adopt — Migrate Existing Project to Standards

Migrate an existing project to use the unified global tooling (hooks, conventions, quality gates, CI). Smart merge that preserves project-specific content while aligning tooling configuration.

## Input

Arguments from command: `$ARGUMENTS`

- `--dry-run`: Preview all changes without writing files. Report what would change.
- No arguments: Apply changes interactively, confirming destructive operations.

## Phase 1: Project Analysis

### 1.1 Stack Detection

Detect the project stack by checking the workspace root:

- **Python**: `pyproject.toml` exists
- **TypeScript**: `package.json` exists
- **Both**: both files exist

### 1.1b Platform Detection

Detect the VCS platform to decide CI configuration:

1. Run `git remote -v` to check for remotes
2. If remote URL contains `gitlab` → GitLab project
3. If remote URL contains `github` → GitHub project
4. If **no remote configured** → assume GitLab (user's default platform), note as "local repo, no remote"
5. If `.gitlab-ci.yml` exists → confirm GitLab
6. If `.github/workflows/` exists → confirm GitHub

Report the detected platform in the analysis. Never assume GitHub just because `.gitlab-ci.yml` is missing — always check the remote first.

### 1.2 Current State Inventory

Read and catalog what already exists:

```
Project Analysis
================
Stack:              <python / typescript / both>
Package name:       <from pyproject.toml or package.json>
Import name:        <python import name or TS src structure>
Platform:           <gitlab / github / local (no remote)>
Remote:             <remote URL or "none">

Existing configs:
  pyproject.toml:       YES/NO  (ruff: X rules, pyright: basic/strict, coverage: X%)
  biome.json:           YES/NO  (rules: default/custom)
  tsconfig.json:        YES/NO  (strict: yes/no)
  .cursor/rules/:       YES/NO
  CONVENTIONS.md:       YES/NO
  .gitlab-ci.yml:       YES/NO  (component version: vX.Y.Z)

Local Cursor config:
  .cursor/hooks.json:                   YES/NO  (has hooks: yes/no)
  .cursor/hooks/:                       YES/NO  (X scripts)
  .cursor/agents/convention-checker:    YES/NO
```

### 1.3 Gap Analysis

Compare current state against golden standards:

For each config file, compare the current version against the template and report:
- **ALIGNED** — already matches the golden config
- **PARTIAL** — exists but missing rules/settings
- **OUTDATED** — exists but uses old versions or patterns
- **MISSING** — does not exist

## Phase 2: Migration Plan

Present a numbered migration plan to the user before making changes:

```
Migration Plan for <project-name>
===================================

1. [CREATE]  CONVENTIONS.md — from template, customized with project exception base
2. [UPDATE]  pyproject.toml — add 12 missing ruff rules, switch pyright to strict, add xenon/vulture
3. [UPDATE]  .gitlab-ci.yml — upgrade pipeline-components v1.7.0 -> v1.9.0
4. [REPLACE] .cursor/hooks.json — point to global hooks
5. [DELETE]  .cursor/hooks/ — 3 scripts (now global)
6. [DELETE]  .cursor/agents/convention-checker.md — now global
7. [UPDATE]  .cursor/rules/ — add quality gates commands, update workflow section
8. [SKIP]    biome.json — not applicable (Python-only project)

Proceed? (y/n)
```

In `--dry-run` mode, show this plan and stop.

## Phase 3: Execute Migration

### 3.1 CONVENTIONS.md

**If missing:** Copy from `~/.cursor/templates/CONVENTIONS.md` and customize:
- Set `base-exception` to the project's actual base exception (scan `exceptions.py` or similar)
- Comment/uncomment TypeScript section based on detected stack
- Preserve any custom rules if migrating from an existing conventions file

**If exists:** Diff against template and report differences. Do NOT overwrite — show the user what sections are missing or different and let them decide.

### 3.2 pyproject.toml (Python)

**Merge strategy — NEVER overwrite the entire file.** Use targeted edits:

#### [tool.ruff] section
- Read the golden template from `~/.cursor/templates/pyproject-python.toml`
- Compare `[tool.ruff.lint] select` lists
- Add missing rule categories (e.g., if project has `["E", "W", "F"]`, add the missing `"S"`, `"B"`, `"UP"`, etc.)
- Add missing `[tool.ruff.lint.per-file-ignores]` for tests if not present
- Set `known-first-party` in `[tool.ruff.lint.isort]` to the project's import name
- Preserve any project-specific `ignore` rules

#### [tool.pyright] section
- If missing, add `typeCheckingMode = "strict"` and correct `pythonVersion`
- If present but not strict, switch to strict

#### [tool.pytest.ini_options] section
- Add `asyncio_mode = "auto"` if missing
- Add `strict-markers` and standard markers if missing
- Preserve existing testpaths and markers

#### [tool.coverage] section
- Set `fail_under = 100` if not already set (warn if currently lower)
- Set `branch = true` if missing
- Set correct `source` path
- Add standard `exclude_lines` if missing

#### [tool.vulture] section
- Add if missing with `min_confidence = 80` and correct paths

#### [tool.codespell] section
- Add if missing with standard config

#### [dependency-groups] dev
- Check for missing quality tools: pyright, ruff, xenon, vulture, codespell, pytest-cov
- Report which need to be added (do NOT remove existing dev dependencies)

### 3.3 biome.json (TypeScript)

**If missing and TypeScript detected:** Copy from `~/.cursor/templates/biome.json`

**If exists:** Compare rules against golden config:
- Report missing strict rules (noExplicitAny, noNonNullAssertion, etc.)
- Show diff and let user decide whether to merge

### 3.4 tsconfig.json (TypeScript)

**If exists:** Check for missing strict flags:
- `noUncheckedIndexedAccess`
- `exactOptionalPropertyTypes`
- `verbatimModuleSyntax`
- `noImplicitOverride`

Report missing flags as suggestions. Do NOT overwrite — TypeScript configs are project-sensitive.

### 3.5 .gitlab-ci.yml

Use the platform detected in Phase 1.1b to decide:

**If platform is GitHub** (remote URL contains github):
- Skip `.gitlab-ci.yml` entirely
- Note: "GitHub Actions not yet covered by this tooling"

**If platform is GitLab OR local (no remote):**

**If `.gitlab-ci.yml` exists:**
- Detect current pipeline-components version (e.g., `@v1.7.0`)
- If outdated, update to latest (`@v1.9.0`)
- Check that all quality gate inputs are enabled (enable_ruff, enable_pyright, enable_xenon, enable_vulture, enable_ruff_format)
- Add missing inputs with correct values
- Set `lint_config_mode: project` if not set

**If `.gitlab-ci.yml` missing:**
- Generate from `~/.cursor/templates/gitlab-ci-snippets.md` using detected package name
- Choose the appropriate template (library-python-pyright for libraries, microservice-python for services)
- If the project has no remote yet, note: "CI config created for GitLab — will be used when remote is added"

### 3.6 .cursor/hooks.json

**Replace entirely** with the template from `~/.cursor/templates/cursor-hooks-project.json`. This file only contains hook references that now point to global scripts.

### 3.7 .cursor/hooks/ (Remove Local Hooks)

If `.cursor/hooks/` exists with local hook scripts:
1. List the scripts that will be removed
2. Verify the global hooks at `~/.cursor/hooks/` cover the same functionality
3. Delete the local hooks directory

The global hooks in `~/.cursor/hooks/` (referenced by `~/.cursor/hooks.json`) now handle:
- `lint-python.sh` — ruff check + format on every Python edit
- `typecheck-python.sh` — pyright on every Python edit
- `lint-typescript.sh` — biome check on every TS/JS edit
- `block-protected-files.sh` — block .env and lock file edits

### 3.8 .cursor/agents/convention-checker.md (Remove Local Agent)

If `.cursor/agents/convention-checker.md` exists locally:
1. Show the user that the global agent at `~/.cursor/agents/convention-checker.md` now handles this
2. Note that the global agent reads the local `CONVENTIONS.md` for project-specific rules
3. Delete the local agent file

### 3.9 .cursor/rules/

**If missing:** Generate from `~/.cursor/templates/cursor-rules-project.mdc` with detected project info.

**If exists:** Merge strategy:
1. **Preserve**: Project Overview, Architecture, Key Design Decisions sections (project-specific content)
2. **Update**: Commands section — ensure all quality gate commands are listed
3. **Update**: Development Workflow section — add SDD pipeline reference if missing
4. **Update**: Git Conventions section — add if missing
5. Show the user a diff of proposed changes before applying

## Phase 4: Validation

After migration, run a quick validation:

### Python
```bash
uv sync                    # ensure deps install
uv run ruff check .        # lint passes
uv run pyright src/        # type check
```

### TypeScript
```bash
npm install                # ensure deps install
npx biome check .          # lint passes
npx tsc --noEmit           # type check
```

Report results:

```
Migration Complete — <project-name>
=====================================

Files created:   X
Files updated:   X
Files deleted:   X

Validation:
  Dependencies:  PASS/FAIL
  Lint:          PASS/FAIL (X issues to fix)
  Type check:    PASS/FAIL (X errors to fix)

Next steps:
  - Fix N lint issues: `uv run ruff check --fix .`
  - Fix N type errors: review pyright output above
  - Review CONVENTIONS.md and customize if needed
  - Run `/quality-gates` for full validation
```

## Important Rules

- **NEVER overwrite project dependencies** — only add missing quality tools to dev deps
- **NEVER overwrite pyproject.toml entirely** — use targeted edits per section
- **NEVER overwrite project-specific sections in .cursor/rules/** — preserve Architecture and Design Decisions
- **NEVER delete files without listing them first** — always show what will be removed
- **Always preserve project-specific ruff ignores** — they exist for a reason
- **Always preserve existing test configuration** — testpaths, markers, fixtures
- **If pyright strict mode introduces too many errors** (>50), suggest a gradual migration: start with `basic` mode and create a task to fix type errors incrementally
- **If coverage threshold is currently below 100%**, warn but set it — the user can adjust later

## Tone

Be transparent about every change. The user should understand exactly what will change and why before any file is modified. When in doubt, preserve existing content and suggest the change instead of applying it.

## Commit

Commit the migration changes:
- Type: `chore`
- Scope: `adopt`
- Example: `chore(adopt): migrate <project-name> to unified tooling`
