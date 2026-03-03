---
name: quality-gates
description: Run all quality gates for the current project and report consolidated pass/fail results
---

# Quality Gates

Run all quality gates for the current project and report a consolidated pass/fail summary.

## Stack Detection

Determine the project stack by checking for configuration files:

### Python Detection
Look for `pyproject.toml`. If found, read it to extract:
1. **Package name** from `[project] name`
2. **Coverage source** from `[tool.coverage.run] source`
3. **Coverage threshold** from `[tool.coverage.report] fail_under` (default: 100)
4. **Vulture whitelist** — check if `vulture_whitelist.py` exists

### TypeScript Detection
Look for `package.json`. If found, check for:
1. **Biome** — `biome` in devDependencies and `biome.json` exists
2. **TypeScript** — `typescript` in devDependencies and `tsconfig.json` exists
3. **Vitest** — `vitest` in devDependencies
4. **Knip** — `knip` in devDependencies
5. **Coverage threshold** — check vitest config or package.json scripts

If both `pyproject.toml` and `package.json` exist, run gates for both stacks.

If neither is found, report an error and stop.

## Execution

Run **all checks independently**. Do not stop on first failure — run every gate and collect all results.

### Python Gates

#### 1. Lint
```bash
uv run ruff check .
```

#### 2. Format
```bash
uv run ruff format --check .
```

#### 3. Type Check
```bash
uv run pyright src/
```

If no `src/` directory, run `uv run pyright .` excluding `.venv`.

#### 4. Tests + Coverage
Use the coverage source and threshold from `pyproject.toml`:
```bash
uv run pytest --cov=<coverage_source> --cov-fail-under=<threshold>
```

#### 5. Complexity
```bash
uv run xenon --max-absolute A --max-modules A --max-average A src/
```

If no `src/` directory, run against `.` excluding `.venv` and `tests`.

#### 6. Dead Code
```bash
uv run vulture --min-confidence 80 src/
```

If `vulture_whitelist.py` exists, append it to the command.

### TypeScript Gates

#### 1. Lint + Format
```bash
npx biome check .
```

If Biome not found but ESLint is configured:
```bash
npx eslint . && npx prettier --check .
```

#### 2. Type Check
```bash
npx tsc --noEmit
```

#### 3. Tests + Coverage
```bash
npx vitest run --coverage
```

If Vitest not found but Jest is configured:
```bash
npx jest --coverage
```

#### 4. Dead Exports
```bash
npx knip
```

If Knip not found, skip with a note.

## Report

Output a summary table per detected stack:

### Python Report

```
Quality Gates -- <package-name> (Python)
========================================
  Lint:       PASS/FAIL
  Format:     PASS/FAIL
  Types:      PASS/FAIL
  Coverage:   PASS/FAIL (XX%)
  Complexity: PASS/FAIL
  Dead Code:  PASS/FAIL
  ----------------------------------------
  Overall:    PASS/FAIL
```

### TypeScript Report

```
Quality Gates -- <project-name> (TypeScript)
=============================================
  Lint+Format: PASS/FAIL
  Types:       PASS/FAIL
  Coverage:    PASS/FAIL (XX%)
  Dead Exports:PASS/FAIL
  ----------------------------------------
  Overall:     PASS/FAIL
```

For any FAIL, show the error output immediately below the table so the issue can be fixed.

### Combined Report (when both stacks detected)

Show both reports sequentially, then a combined verdict:

```
Combined Verdict: PASS/FAIL
  Python:     PASS/FAIL (X/6 gates)
  TypeScript: PASS/FAIL (X/4 gates)
```
