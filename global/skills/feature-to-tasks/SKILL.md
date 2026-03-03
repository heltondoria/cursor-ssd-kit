---
name: feature-to-tasks
description: Generate a TDD-structured task list from a feature spec
argument-hint: <path-to-feature-spec> (e.g., ".specs/F6-task-export.md")
---

# Feature Spec to Task List Generator

Generate a TDD-structured implementation plan from a feature specification document (produced by `/feature-spec`). Each feature method becomes a red-green cycle: write the failing test first, then implement until it passes.

**Pipeline position**: `/discovery` (optional) -> `/discovery-review` -> `/prd` -> `/prd-review` -> `/feature-spec` -> **`/feature-to-tasks`** -> `/task-review` -> implement

## Input

Feature spec path from arguments: `$ARGUMENTS`

If no argument is provided, search for `.specs/*.md` files in the workspace and ask the user which spec to process.

## Reference Documents

Before generating tasks, also read:

1. The feature spec file (provided as argument)
2. `.cursor/rules/ (project rules)` — project commands and conventions
3. `CONVENTIONS.md` (if exists) — code conventions
4. `pyproject.toml` or `package.json` — to detect stack and tooling

## Stack Detection

Detect the project stack to generate appropriate quality gate commands:

- **Python**: presence of `pyproject.toml` with `[tool.ruff]` or `[tool.pyright]`
- **TypeScript**: presence of `package.json` with `biome` or `typescript` in devDependencies
- **Both**: generate tasks for both stacks

## Feature Spec Analysis

### Step 1: Extract TDD Boundaries

From the feature spec, extract every method signature in § 4 (Internal Interfaces). Each method is a TDD boundary:

1. **Method signature** — name, parameters, return type
2. **Raises clause** — exception types
3. **Test scenarios** — from § 6, match scenarios to the method they test

### Step 2: Extract Non-TDD Tasks

Some tasks don't follow the test-first pattern:

1. **Schema/model changes** — Altering data models, adding fields, migration SQL (§ 2.1, § 8.3)
2. **Configuration/wiring** — DI registration, router mounting, MCP tool registration
3. **API endpoint tasks** — REST endpoints that delegate to tested service methods
4. **Frontend tasks** — UI components, state management, API client functions

### Step 3: Extract Event-Driven Tasks (if § 9 exists)

If the feature spec has a § 9 (Async Messaging), also extract:

1. **Event schema definitions** — Pydantic models for each event (§ 9.3)
2. **Event producer wiring** — Publishing events from service methods
3. **Event consumer handlers** — Handler functions with idempotency logic
4. **Channel/topic configuration** — Broker setup if needed
5. **Event integration tests** — Producer emits → consumer receives → side effect verified

## Task Format

Use ralph-compatible markdown checkboxes:

```markdown
- [ ] <Action verb> <target> in `<file>` -- <specific details>
```

Each task must be:
- **Deterministic** — single, unambiguous expected outcome
- **Verifiable** — can be validated by running a command
- **Objective** — no subjective judgment needed
- **Atomic** — completable in one focused session

## TDD Task Structure

**For each method in § 4 (Internal Interfaces), generate a RED-GREEN pair:**

```markdown
- [ ] Write failing tests for `method_name` in `tests/<test_file>.py` -- Test scenarios: <list from § 6 that target this method>. Assert signatures, return types, exceptions. Tests must FAIL (RED) because the method does not exist yet.
- [ ] Implement `method_name` in `src/<package>/<file>.py` -- <signature from § 4>. <behavior summary>. All tests from previous task must PASS (GREEN).
```

**The RED task always comes before the GREEN task.** This ensures:
1. Tests define the contract before code exists
2. Implementation is driven by test expectations
3. Passing tests prove the method works
4. Regressions are caught immediately if a later task breaks an earlier method

**For refactoring phases (when applicable), add a REFACTOR step:**

```markdown
- [ ] Refactor `module_name` -- <what to improve>. All existing tests must still PASS.
```

## Output Structure

```markdown
# Fix Plan — F{N}: {Feature Name}

## High Priority

### Phase 1: Foundation — Models & Schema

- [ ] <model/schema/migration tasks — no TDD, these are structural>
- [ ] Run quality gates: `<lint + format + type check>`

### Phase 2: Core Logic — TDD Cycles

[For each method, a RED-GREEN pair]

- [ ] RED: Write failing tests for `method_a` in `tests/test_<module>.py` -- Scenarios: <list>
- [ ] GREEN: Implement `method_a` in `src/<package>/<module>.py` -- <signature, behavior>
- [ ] RED: Write failing tests for `method_b` in `tests/test_<module>.py` -- Scenarios: <list>
- [ ] GREEN: Implement `method_b` in `src/<package>/<module>.py` -- <signature, behavior>
- [ ] Run full quality gates: `<all gates>`

### Phase 3: Integration — API & Wiring

- [ ] <REST endpoint / MCP tool / DI wiring tasks>
- [ ] RED: Write integration tests in `tests/test_<integration>.py` -- <scenarios>
- [ ] GREEN: Wire endpoints/tools to pass integration tests
- [ ] Run full quality gates: `<all gates>`

## Medium Priority

### Phase 4: Events (if § 9 exists)

- [ ] Define event schemas in `src/<package>/events/<file>.py` -- <schema names from § 9.3>
- [ ] RED: Write event producer tests -- <verify events are emitted on triggers from § 9.1>
- [ ] GREEN: Implement event publishing in service methods
- [ ] RED: Write event consumer tests -- <verify handlers process events idempotently from § 9.2>
- [ ] GREEN: Implement event consumer handlers
- [ ] Run full quality gates: `<all gates>`

### Phase 5: Frontend (if applicable)

- [ ] <types, API client, state, component tasks>
- [ ] <frontend test tasks>
- [ ] Run frontend quality gates: `<frontend gates>`

## Notes

### Key Design Decisions
- **<decision>** — <rationale from spec § 2.3>

### TDD Rationale
Each RED-GREEN pair targets one method from the feature spec § 4.
Tests are written against the method signature and test scenarios from § 6.
Implementation is minimal — just enough to make the tests pass.

### Implementation Order Rationale
1. <first> — <why>
```

## Phase Ordering Rules

**High Priority (must complete first):**
1. **Foundation** — data models, schema migrations, exception classes. No TDD needed — these are structural. Quality gate: lint + format + type check.
2. **Core Logic (TDD)** — RED-GREEN pairs for every method in § 4. Each pair produces tested, working code. Quality gate: full gates including tests + coverage.
3. **Integration** — REST endpoints, MCP tools, DI wiring. Integration tests validate the full stack. Quality gate: full gates.

**Medium Priority (feature-complete):**
4. **Events** — event schemas, producers, consumers, integration tests. Only if § 9 exists.
5. **Frontend** — types, API client, state management, components, frontend tests.

**Low Priority (polish):**
6. **Edge cases & hardening** — additional edge case tests beyond § 6.2 if needed.

## Task Detail Rules

### For RED (test) tasks:
- Name the test file path explicitly
- List specific test scenarios from § 6 that target this method
- Include the assertion pattern (e.g., "assert result.scope == 'auth'", "assert raises NodeNotFoundError")
- The test MUST reference the method signature from § 4 even though the method doesn't exist yet

### For GREEN (implementation) tasks:
- Name the target file explicitly
- Include the full method signature from § 4
- Reference "all tests from previous RED task must pass"
- Do NOT add new test scenarios in GREEN tasks — tests were already written

### For structural tasks (models, schema, wiring):
- Name the target file explicitly
- Include exact field names, types, SQL, or configuration
- These don't need RED-GREEN pairs — they are verified by quality gates (lint, type check)

### For event tasks (if applicable):
- Event schema tasks include full Pydantic model from § 9.3
- Producer tests verify the event is emitted with correct payload
- Consumer tests verify idempotency (processing the same event twice has no additional effect)

## Output Location

Write the generated task list to: `.ralph/fix_plan-F{N}.md` in the workspace root, where `F{N}` is the feature ID extracted from the spec header (e.g., `F6`, `F7`).

Examples:
- `.specs/F6-task-export.md` → `.ralph/fix_plan-F6.md`
- `.specs/F7-scope-management.md` → `.ralph/fix_plan-F7.md`

If `.ralph/` directory does not exist, create it.

If the user specifies a different output path, use that instead.

## Rules

1. **Name every file** — use exact paths (`src/kaos_designer/export/task_list.py`)
2. **Name every class and method** — include parameters and return types from § 4
3. **Name every test scenario** — use `test_<fn>_<scenario>_<result>` naming
4. **RED before GREEN** — every method gets its test task BEFORE its implementation task
5. **One test file per task** — keeps tasks atomic
6. **Quality gate at end of each phase** — no exceptions
7. **Do NOT include Future Expansion items**
8. **Do NOT include tasks for features other than the one specified**
9. **Do NOT duplicate test scenarios** — each scenario from § 6 appears in exactly one RED task

## Tone

Be precise and mechanical. Every task must be unambiguous — an AI agent should execute each task without interpretation or judgment calls. The RED-GREEN structure makes the workflow self-correcting: if a GREEN task doesn't pass the RED tests, the agent knows immediately.
