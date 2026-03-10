# cursor-ssd-kit

A curated set of Cursor IDE configuration files that implement **Specification-Driven Development (SDD)** — a structured pipeline from discovery through PRD, feature specs, TDD task generation, implementation, and quality validation.

Copy to `~/.cursor/` for structured, TDD-first workflows in any Python or TypeScript project.

## Prerequisites

- **Cursor** 2.4+
- **Python**: `uv` package manager, Python 3.12+
- **TypeScript**: `npm` or `pnpm`, Node.js 18+

## Installation

### Quick Install

```bash
bash install.sh
```

This will:
1. Back up your existing `~/.cursor/` configuration (if any)
2. Copy all rules, skills, hooks, agents, templates, and scripts to `~/.cursor/`
3. Make hook scripts executable
4. Report a summary of installed components

### Manual Install

```bash
# Back up existing config
cp -r ~/.cursor ~/.cursor.bak-$(date +%Y%m%d)

# Copy components
mkdir -p ~/.cursor
cp -r global/rules ~/.cursor/
cp -r global/skills ~/.cursor/
cp -r global/hooks ~/.cursor/
cp -r global/agents ~/.cursor/
cp -r global/templates ~/.cursor/
cp -r global/scripts ~/.cursor/
cp global/hooks.json ~/.cursor/

# Make hooks executable
chmod +x ~/.cursor/hooks/*.sh
```

## What's Included

### SDD Pipeline

```
/discovery ──> /discovery-review ──> /prd ──> /prd-review
                                      │             (or /prd-import)
                              /feature-spec <─────┘
                                    │
                              /traceability (optional)
                                    │
                              /feature-review
                                    │
                              /feature-to-tasks
                                    │
                              /task-review
                                    │
                              implement (TDD)
                                    │
                              /quality-gates
                                    │
                              /impl-review
                                    │
                              /release
```

### Skills (15)

| Skill | Purpose |
|-------|---------|
| `/discovery` | Discover the WHY behind a project (Golden Circle) |
| `/discovery-review` | Validate discovery document completeness (6 criteria) |
| `/prd` | Create PRD through guided questioning |
| `/prd-import` | Import external PRD into SDD format |
| `/prd-review` | Validate PRD completeness (13 criteria) |
| `/feature-spec` | Refine a single PRD feature into detailed implementation spec |
| `/traceability` | Analyze BR/SR cross-references between PRD and feature specs |
| `/feature-review` | Validate feature spec quality (9 criteria) |
| `/feature-to-tasks` | Generate TDD-structured task list from a feature spec |
| `/task-review` | Validate task list quality and spec coverage |
| `/quality-gates` | Run all quality checks and report pass/fail |
| `/impl-review` | Validate implementation against feature spec with scoring |
| `/scaffold` | Create new project with full tooling setup |
| `/adopt` | Migrate existing project to unified tooling standards |
| `/release` | Create a semver release with version bump, changelog, and git tag |

### Rules (6)

Global rules applied to all projects:

| Rule | Scope |
|------|-------|
| `sdd-philosophy.mdc` | Always — SDD pipeline and methodology |
| `python-standards.mdc` | `**/*.py` — Python quality standards |
| `typescript-standards.mdc` | `**/*.{ts,tsx}` — TypeScript quality standards |
| `security-layers.mdc` | Always — Security pipeline layers |
| `git-conventions.mdc` | Always — Branch naming, commit messages, platform |
| `available-skills.mdc` | Always — Skills and agents reference |

### Hooks (4)

| Hook | Trigger | Purpose |
|------|---------|---------|
| `lint-python.sh` | After file edit (`*.py`) | Auto-fix lint + format with ruff |
| `typecheck-python.sh` | After file edit (`*.py`) | Type check with pyright |
| `lint-typescript.sh` | After file edit (`*.{ts,tsx,js,jsx}`) | Auto-fix lint with Biome/ESLint |
| `block-protected-files.sh` | Before tool use (`*.{env,lock}`) | Prevent editing sensitive files |

### Agents (2)

| Agent | Purpose |
|-------|---------|
| `convention-checker` | Check code against project CONVENTIONS.md |
| `security-bug-reviewer` | Detect security vulnerabilities and bug patterns with CWE-specialized analysis |

### Templates (7)

| Template | Purpose |
|----------|---------|
| `cursor-rules-project.mdc` | Project rules template (overview, commands, architecture) |
| `cursor-hooks-project.json` | Project hooks configuration |
| `CONVENTIONS.md` | Code conventions template |
| `pyproject-python.toml` | Golden Python config (ruff 35+ rules, pyright strict) |
| `tsconfig-strict.json` | Strict TypeScript config |
| `biome.json` | Biome v2 strict linter+formatter config |
| `gitlab-ci-snippets.md` | GitLab CI pipeline reference |

### Scripts (1)

| Script | Purpose |
|--------|---------|
| `sdd-metrics.py` | Extract SDD pipeline metrics from git history |

## Pipeline Metrics

Run `python ~/.cursor/scripts/sdd-metrics.py` to extract pipeline metrics from git history.
Requires conventional commits with feature ID scopes (e.g., `feat(F6): ...`).

```bash
python ~/.cursor/scripts/sdd-metrics.py                      # Full report
python ~/.cursor/scripts/sdd-metrics.py --json               # Machine-readable output
python ~/.cursor/scripts/sdd-metrics.py --feature F6         # Single feature
python ~/.cursor/scripts/sdd-metrics.py --period 2026-01:2026-03
```

## Supported Stacks

### Python
- **Linter**: ruff (35+ rules, S rules for security)
- **Formatter**: ruff format
- **Type checker**: pyright strict mode
- **Tests**: pytest + pytest-cov (100% coverage)
- **Complexity**: xenon grade A
- **Dead code**: vulture (80+ confidence)
- **Typos**: codespell

### TypeScript
- **Linter + Formatter**: Biome v2 (strict)
- **Type checker**: tsc strict mode
- **Tests**: Vitest + @vitest/coverage-v8 (90%+)
- **Dead exports**: Knip
- **Typos**: codespell

## Differences from claude-code-sdd-kit

This kit is a Cursor-compatible adaptation of [claude-code-sdd-kit](https://github.com/helton/claude-code-sdd-kit). Key differences:

| Aspect | claude-code-sdd-kit | cursor-ssd-kit |
|--------|--------------------:|---------------:|
| Target | Claude Code CLI | Cursor IDE 2.4+ |
| Global config | `~/.claude/CLAUDE.md` | `~/.cursor/rules/*.mdc` |
| Project config | `CLAUDE.md` | `.cursor/rules/project.mdc` |
| Hooks config | `settings.json` (Claude format) | `hooks.json` (Cursor format) |
| Hook events | `PostToolUse`/`PreToolUse` | `afterFileEdit`/`preToolUse` |
| Hook timeouts | Milliseconds | Seconds |
| File path var | `$CLAUDE_FILE_PATH` | `${CURSOR_FILE_PATH:-${FILE_PATH:-$1}}` |
| Agent format | Plain markdown | YAML frontmatter |
| Plugins | `enabledPlugins` section | N/A (Cursor handles extensions separately) |

## License

MIT
