---
name: impl-review
description: Validate a project implementation against its feature spec and produce an adherence report with scoring
argument-hint: <impl-path> <spec-path> (e.g., "src/ .specs/F6-task-export.md")
---

# Implementation Review

Validate that a project implementation correctly covers all requirements defined in its feature spec (produced by `/feature-spec`). Produces an adherence report with justified conclusions for each requirement.

## Input

Arguments from command: `$ARGUMENTS`

Expected format: `<implementation-folder> <spec-file-path>`

Examples:
- `src/ .specs/F6-task-export.md`
- `. .specs/F7-scope-management.md` (current directory)

If no arguments are provided, search for `.specs/*.md` files and ask the user which spec to validate against. If no spec exists, ask the user for the path.

## Reference Documents

Before reviewing, read:

1. The feature spec file (primary validation source)
2. `.cursor/rules/ (project rules)` from workspace root — project overview and architecture
3. `CONVENTIONS.md` from workspace root (if exists) — code conventions
4. The PRD file (for broader context) — look for `PRD-*.md` in workspace root

## Review Process

### Phase 1: Feature Spec Requirement Extraction

Read the feature spec and extract a **complete requirement inventory**:

#### 1.1 Internal Interfaces (§ 4)
- Every method signature: name, parameters, return type, raises clause
- These are the primary TDD boundaries

#### 1.2 API Contract (§ 3)
- Every endpoint: method, path, request/response schemas, error responses

#### 1.3 Component Architecture (§ 2.1)
- All files listed as `[NEW]` or `[EXISTING — modify]`

#### 1.4 Error Scenarios (§ 5)
- Every error path: trigger, exception type, HTTP code, recovery

#### 1.5 Test Scenarios (§ 6)
- All happy path, edge case, and error case scenarios

#### 1.6 Async Messaging (§ 9, if present)
- Event schemas, producers, consumers, delivery guarantees

**IMPORTANT:** Only validate what is in the feature spec scope. Do NOT check requirements from other features or PRD sections outside this feature.

### Phase 2: Implementation Scan

Scan the implementation folder to build an inventory of what exists:

#### 2.1 Project Structure
- Read `pyproject.toml` or `package.json` for metadata and dependencies
- List all source files
- List all test files
- Check for type markers (`py.typed`, `tsconfig.json`)
- Check for exports (`__init__.py` with `__all__`, or `index.ts`)

#### 2.2 Source Code Analysis

For each source module, read and extract:
- All public classes, functions, constants
- Exception classes and hierarchy
- Config models and their fields
- Async vs sync signatures
- Docstring presence and style
- Import patterns

#### 2.3 Test Coverage Analysis

For each test file:
- Extract test function names
- Map tests to spec requirements by naming convention
- Check for integration tests
- Check for fixtures

#### 2.4 Configuration Analysis
- Verify tooling config matches project standards (ruff/pyright/biome/tsc)
- Coverage settings present and correct
- Dev dependencies include all quality tools

### Phase 3: Requirement-by-Requirement Verification

For each requirement extracted from the feature spec, determine status:

**IMPLEMENTED** — Fully present with correct signatures, type hints, tests, and docstrings
**PARTIAL** — Exists but incomplete (missing parameters, tests, or docstrings vs spec)
**MISSING** — Not found in the codebase
**DIVERGENT** — Exists but contradicts the spec (different signature, behavior, or location)

### Phase 4: Convention Compliance Check

Verify the implementation follows project conventions from `CONVENTIONS.md`:

1. **Type hints** — correct syntax per conventions
2. **Docstrings** — correct style on all public API
3. **Exceptions** — `from e` chaining in all `except` blocks
4. **Logging** — structured logging per conventions
5. **Config models** — frozen, with Field descriptions
6. **Async** — I/O operations match async requirements from spec § 8.1
7. **Imports** — correct ordering
8. **Test naming** — follows convention pattern

## Output Format

```
Implementation Review -- <project-name>
Feature Spec: <spec filename>
========================================

Package Structure:           PASS / PARTIAL / MISSING
Internal Interfaces (§ 4):  PASS / PARTIAL / MISSING
API Contract (§ 3):         PASS / PARTIAL / MISSING
Error Handling (§ 5):       PASS / PARTIAL / MISSING
Test Coverage (§ 6):        PASS / PARTIAL / MISSING
Convention Compliance:       PASS / PARTIAL / MISSING
Quality Gate Readiness:      PASS / PARTIAL / MISSING
----------------------------------------
Overall Adherence:           X/Y requirements implemented (Z%)
```

### Requirement Adherence Detail

```
Spec Requirement              | Status      | Evidence / Justification
------------------------------|-------------|----------------------------------
§ 4: method_name()            | IMPLEMENTED | Found in <file>:<line>. Tests in
                              |             | <test_file>. Signature matches.
§ 4: other_method()           | PARTIAL     | Method exists but missing param
                              |             | `timeout` from spec § 4.
§ 3: POST /api/v1/resource    | MISSING     | No matching endpoint found.
§ 5: InvalidInputError        | DIVERGENT   | Spec specifies 422 but impl
                              |             | returns 400 at <file>:<line>.
```

### Convention Violations

```
1. [CATEGORY] <file>:<line> -- <description>
2. [CATEGORY] <file>:<line> -- <description>
```

### Missing Test Scenarios

```
Spec Test Scenario (§ 6)            | Test File        | Status
------------------------------------|------------------|--------
§ 6.1 #1: happy path create        | test_core.py:15  | COVERED
§ 6.2 #3: empty input edge case    | --               | MISSING
§ 6.3 #2: not found error          | test_core.py:45  | COVERED
```

### Recommendations

For each PARTIAL, MISSING, or DIVERGENT item:
- What specifically needs to be added or changed
- The spec section that defines the expected behavior
- A concrete code suggestion when helpful

## Scoring

Calculate adherence scores:

- **Requirement adherence**: `IMPLEMENTED / total requirements * 100%`
- **Test scenario coverage**: `COVERED / total scenarios * 100%`
- **Convention compliance**: `clean items / total checked * 100%`
- **Overall score**: weighted average — 50% requirements, 30% tests, 20% conventions

```
Final Score
========================================

Requirement Adherence:  85% (17/20 implemented)
Test Scenario Coverage: 90% (18/20 covered)
Convention Compliance:  95% (38/40 clean)
----------------------------------------
Overall Score:          89% (weighted)

Verdict: PARTIAL -- 3 requirements and 2 test scenarios need attention
```

Verdict thresholds:
- **100%**: COMPLETE — All spec requirements implemented and verified
- **90-99%**: NEAR-COMPLETE — Minor gaps, ready for final polish
- **70-89%**: PARTIAL — Significant requirements missing
- **<70%**: INCOMPLETE — Major implementation gaps

## Tone

Be precise, evidence-based, and constructive. Every conclusion must cite specific files, line numbers, and spec sections. The goal is an actionable gap analysis.
