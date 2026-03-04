---
name: scaffold
description: Scaffold a new project with standard directory structure, config files, CI, and quality tooling
argument-hint: <project-name> [--stack python|typescript|both] (e.g., "my-api --stack python")
---

# Project Scaffolding

Create a complete, standards-compliant project from scratch with all quality tooling configured.

## Input

Arguments from command: `$ARGUMENTS`

Parse the arguments:
- **project-name** (required): The project name (lowercase, alphanumeric with hyphens)
- **--stack** (optional): `python`, `typescript`, or `both`. Default: `python`

If no argument is provided, ask the user for the project name and stack.

## Pre-Flight Checks

1. Validate the project name: lowercase, alphanumeric with hyphens, no underscores
2. Derive names:
   - **Directory**: `<project-name>/`
   - **Python import**: replace hyphens with underscores (e.g., `my_api`)
   - **PascalCase**: for class names (e.g., `MyApi`)
3. Check that the target directory does NOT already exist. If it does, abort with an error.
4. Read the golden template files from `~/.cursor/templates/`:
   - `pyproject-python.toml` (for Python stack)
   - `biome.json` (for TypeScript stack)
   - `tsconfig-strict.json` (for TypeScript stack)
   - `CONVENTIONS.md` (template to customize)
   - `cursor-rules-project.mdc` (template for project rules)
   - `gitlab-ci-snippets.md` (for CI reference)

## Python Project Structure

```
<project-name>/
├── src/
│   └── <import_name>/
│       ├── __init__.py
│       ├── py.typed
│       ├── core.py
│       ├── config.py
│       └── exceptions.py
├── tests/
│   ├── __init__.py
│   └── conftest.py
├── pyproject.toml
├── .cursor/
│   └── rules/
│       └── project.mdc
├── CONVENTIONS.md
└── .gitlab-ci.yml
```

### File Contents

**`src/<import_name>/__init__.py`**
```python
"""<project-name> -- <ask user for one-line description>."""

__all__: list[str] = []
```

**`src/<import_name>/py.typed`** — Empty file (PEP 561 marker)

**`src/<import_name>/core.py`**
```python
"""Core module for <project-name>."""
```

**`src/<import_name>/config.py`**
```python
"""Configuration models for <project-name>."""

from pydantic import BaseModel


class <PascalName>Config(BaseModel, frozen=True):
    """Configuration for <project-name>.

    Attributes:
        enabled: Whether the component is enabled.
    """

    enabled: bool = True
```

**`src/<import_name>/exceptions.py`**
```python
"""Exception hierarchy for <project-name>."""


class <PascalName>Error(Exception):
    """Base exception for <project-name>."""
```

**`tests/__init__.py`** — Empty file

**`tests/conftest.py`**
```python
"""Shared test fixtures for <project-name>."""
```

**`pyproject.toml`** — Use the golden template from `~/.cursor/templates/pyproject-python.toml`, replacing:
- `<package-name>` with the project name
- `<package_name>` with the import name
- `<description>` with the user-provided description

**`.gitlab-ci.yml`** — Use the library-python-pyright snippet from `~/.cursor/templates/gitlab-ci-snippets.md`, replacing `<package_name>` with the import name

**`.cursor/rules/project.mdc`** — Use the template from `~/.cursor/templates/cursor-rules-project.mdc`, replacing placeholders

**`CONVENTIONS.md`** — Copy from `~/.cursor/templates/CONVENTIONS.md`, set the base exception name to `<PascalName>Error`

## TypeScript Project Structure

```
<project-name>/
├── src/
│   └── index.ts
├── tests/
│   └── index.test.ts
├── package.json
├── tsconfig.json
├── biome.json
├── .cursor/
│   └── rules/
│       └── project.mdc
├── CONVENTIONS.md
└── .gitlab-ci.yml
```

### File Contents

**`src/index.ts`**
```typescript
// <project-name> -- <description>
export {}
```

**`tests/index.test.ts`**
```typescript
import { describe, it, expect } from 'vitest'

describe('<project-name>', () => {
  it('should be true', () => {
    expect(true).toBe(true)
  })
})
```

**`package.json`** — Standard package.json with:
- `typescript`, `@biomejs/biome`, `vitest`, `@vitest/coverage-v8`, `knip` as devDependencies
- Scripts: `check`, `typecheck`, `test`, `test:coverage`

**`tsconfig.json`** — Copy from `~/.cursor/templates/tsconfig-strict.json`

**`biome.json`** — Copy from `~/.cursor/templates/biome.json`

**`.cursor/rules/project.mdc`** — Adapted from template with TypeScript commands

**`CONVENTIONS.md`** — Copy from template with TypeScript rules uncommented, Python rules commented out

## Both Stacks (Monorepo)

```
<project-name>/
├── backend/
│   └── (python structure above)
├── frontend/
│   └── (typescript structure above)
├── .cursor/
│   └── rules/
│       └── project.mdc
└── CONVENTIONS.md
```

For monorepo, create a root `.cursor/rules/project.mdc` that references both sub-projects.

## Post-Scaffold Steps

After creating all files:

### Python
1. Run `cd <project-name> && uv sync` to validate setup
2. Run `uv run ruff check .` to verify lint passes
3. Run `uv run pyright src/` to verify type checking passes

### TypeScript
1. Run `cd <project-name> && npm install` to install dependencies
2. Run `npx biome check .` to verify lint passes
3. Run `npx tsc --noEmit` to verify type checking passes

Report success with a summary of created files and any post-scaffold instructions.

## Reminders

- Do NOT initialize a git repo — the user manages git separately
- Do NOT create a PRD — the user can use `/prd` for that separately
- Ask the user for a one-line description before generating files

## Commit

Commit the scaffolded project:
- Type: `chore`
- Scope: `scaffold`
- Example: `chore(scaffold): create project structure for <project-name>`
