---
name: feature-review
description: Review a feature spec against quality criteria, PRD alignment, and codebase consistency
argument-hint: <path-to-spec> (e.g., ".specs/F7-scope-management.md" or leave empty to select)
---

# Feature Spec Review

Validate a feature specification against quality standards, PRD alignment, and codebase consistency. This ensures the spec is ready for task generation via `/feature-to-tasks`.

**Pipeline position**: `/discovery` (optional) -> `/discovery-review` -> `/prd` -> `/prd-review` -> `/feature-spec` -> **`/feature-review`** -> `/feature-to-tasks` -> `/task-review` -> implement

## Input

Spec file path from arguments: `$ARGUMENTS`

If no argument is provided, search for `.specs/*.md` files in the workspace and ask the user which one to review.

## Phase 1: Gather Context

Before reviewing, read these files:

1. **The spec file** — the document under review
2. **The PRD** — extract the matching feature section (by feature ID from the spec header). Look for `PRD-*.md` in workspace root.
3. **`.cursor/rules/ (project rules)`** — project overview, architecture, commands
4. **`CONVENTIONS.md`** (if exists) — code conventions

Then **explore the codebase** to verify claims in the spec:

- Read every file listed in § 2.1 (Component Architecture) that is marked `[EXISTING — modify]`
- Verify that method names, class names, and module paths referenced in the spec actually exist (or correctly identify gaps)
- Check that the data model in § 4 is consistent with existing code patterns

This codebase exploration is **mandatory** — do NOT skip it. Many defects are only detectable by comparing the spec against the actual code.

## Phase 2: Evaluate Checklist

### 1. PRD Alignment

Cross-reference the spec against the PRD feature section:

- [ ] **AC coverage**: Every AC listed in the PRD that belongs to backend is addressed (covered directly OR explicitly deferred with rationale)
- [ ] **ACs correctly deferred**: Deferred ACs cite a valid reason (frontend-only, nice-to-have, depends on another feature)
- [ ] **Endpoints match**: API endpoints in spec § 3 match the PRD endpoint table for this feature
- [ ] **Error scenarios match**: Spec § 5 covers all error rows from PRD § 6.3 for this feature
- [ ] **Async/sync alignment**: Spec § 8.1 matches PRD § 12.1 for this feature
- [ ] **Logging events match**: Spec § 8.2 covers events from PRD § 12.2 for this feature
- [ ] **No PRD contradictions**: Spec does not contradict any PRD requirement (e.g., different default value, missing endpoint, wrong HTTP method)

### 2. Spec Completeness (Template Compliance)

Verify all required sections exist and contain substantive content:

- [ ] **§ 1 Summary** — Has What, Why, and PRD ACs list
- [ ] **§ 2.1 Component Architecture** — Lists files with `[NEW]` or `[EXISTING — modify]` tags
- [ ] **§ 2.2 Data Flow** — Shows input → processing → output for each operation
- [ ] **§ 2.3 Key Design Decisions** — Table with columns: Decision, Choice, Rationale, Alternatives rejected. At least 3 decisions documented.
- [ ] **§ 3 API Contract** — Every endpoint has request schema, success response, and error responses with HTTP codes
- [ ] **§ 4 Internal Interfaces** — Method signatures with full type hints, docstrings, Args, Returns, and Raises
- [ ] **§ 5 Error Scenarios** — Table with columns: #, Trigger, Input example, Exception, HTTP, Recovery
- [ ] **§ 6 Test Scenarios** — Reference data defined; Happy path, Edge cases, and Error cases tables populated
- [ ] **§ 7 Integration Points** — Both "consumes" and "consumed by" tables populated
- [ ] **§ 8 Convention Compliance** — Async/Sync table, Logging events table, SQL migration (if applicable)
- [ ] **§ 9 Async Messaging** — Present only if feature uses async events; absent if purely request/response

### 3. Internal Consistency

Check that the spec is internally coherent:

- [ ] **§ 4 ↔ § 3**: Every API endpoint in § 3 maps to at least one method in § 4
- [ ] **§ 4 ↔ § 5**: Every `Raises` clause in § 4 has a matching row in § 5
- [ ] **§ 5 ↔ § 6.3**: Every error scenario in § 5 has a corresponding test in § 6.3
- [ ] **§ 6.1 ↔ § 4**: Every method in § 4 has at least one happy path test in § 6.1
- [ ] **§ 6 reference data ↔ scenarios**: Test scenarios reference entities from the reference data (no phantom entities)
- [ ] **§ 2.1 ↔ § 4**: Every file in the architecture has at least one method in § 4, and vice versa
- [ ] **§ 8.2 ↔ § 4**: Every state-changing method has a logging event
- [ ] **Method signatures consistent**: Return types, parameter names, and exception types are consistent between repository and service layer signatures

### 4. Codebase Consistency

Verify the spec is grounded in the actual codebase:

- [ ] **File paths exist**: Files marked `[EXISTING — modify]` actually exist at the stated paths
- [ ] **Method patterns match**: New methods follow existing naming patterns (e.g., `async def verb_noun()`)
- [ ] **Exception types exist**: All exceptions referenced in § 5 exist in the exception hierarchy or are marked as new
- [ ] **Model fields compatible**: New fields are compatible with existing model patterns (frozen, Field() with defaults)
- [ ] **SQL compatible**: Migration DDL is compatible with existing schema (table names, column types, FK references)
- [ ] **Repository pattern**: New repository methods follow the existing `_conn.execute()` pattern
- [ ] **Service pattern**: New service methods follow the existing `async def` + `self._repository` pattern
- [ ] **Router pattern**: New endpoints follow existing DishkaRoute + FromDishka pattern
- [ ] **Import compatibility**: New exports won't cause circular imports

### 5. Design Decision Quality

Evaluate the design decisions in § 2.3:

- [ ] **Minimum 3 decisions**: Non-trivial features should have at least 3 decisions
- [ ] **Each has rationale**: Not just "chose X" but "chose X because Y"
- [ ] **Each has rejected alternatives**: Shows that alternatives were considered
- [ ] **No premature optimization**: Decisions are driven by current needs, not hypothetical futures
- [ ] **Backward compatible**: Decisions don't break existing functionality (especially for data model changes)
- [ ] **Migration strategy clear**: If changing stored data, the migration path is defined

### 6. Test Scenario Coverage

Verify test scenarios are comprehensive:

- [ ] **Happy path per method**: Every method in § 4 has at least one happy path scenario
- [ ] **Edge cases meaningful**: Edge cases test real boundary conditions, not trivial variations
- [ ] **Error cases per exception**: Every distinct exception in § 5 has at least one test
- [ ] **Reference data sufficient**: Reference dataset contains enough entities to cover all scenarios without invention
- [ ] **No missing boundary**: Boundary conditions identified (empty list, single item, duplicates, max values)
- [ ] **Integration scenarios**: At least one scenario tests cross-layer behavior (e.g., "roundtrip via save/load")

### 7. Feature Boundary Clarity

Verify the spec explicitly delineates what is IN and OUT of scope:

- [ ] **In-scope clear**: Summary and design sections make it clear what this feature implements
- [ ] **Deferred items explicit**: Each AC not covered is listed with its deferral target (e.g., "AC3 → F8 frontend")
- [ ] **No scope creep**: Spec doesn't implement functionality belonging to other features
- [ ] **Dependencies declared**: § 7.1 lists all features this one depends on
- [ ] **Consumers declared**: § 7.2 lists all features that will use this one's outputs

### 8. Spec Size and Focus

Validate the spec follows the template rules:

- [ ] **150-300 lines**: Spec is within target range (under 150 = missing content, over 300 = over-specifying)
- [ ] **No PRD repetition**: Spec references PRD sections instead of copying AC text or descriptions verbatim
- [ ] **Every section adds value**: No section is a mere restatement of the PRD — each adds implementation detail

## Phase 3: Output

### Summary Table

```
Feature Spec Review -- <spec filename>
PRD Feature: <feature ID and name>
========================================

  1.  PRD Alignment:            PASS / PARTIAL / FAIL
  2.  Spec Completeness:        PASS / PARTIAL / FAIL
  3.  Internal Consistency:     PASS / PARTIAL / FAIL
  4.  Codebase Consistency:     PASS / PARTIAL / FAIL
  5.  Design Decisions:         PASS / PARTIAL / FAIL
  6.  Test Coverage:            PASS / PARTIAL / FAIL
  7.  Feature Boundaries:       PASS / PARTIAL / FAIL
  8.  Spec Size & Focus:        PASS / PARTIAL / FAIL
  ----------------------------------------
  Overall:                      X/8 PASS
```

Scoring:
- **PASS**: All checklist items satisfied
- **PARTIAL**: Most items satisfied but 1-2 minor gaps
- **FAIL**: Significant gaps that would cause problems in task generation

### Detailed Findings

For each PARTIAL or FAIL item, provide:

```
[CATEGORY] § <section>
  Issue: <specific problem found>
  Evidence: <what the spec says vs what was expected>
  Fix: <concrete suggestion with example text>
```

Categories: `PRD-ALIGN`, `COMPLETENESS`, `CONSISTENCY`, `CODEBASE`, `DESIGN`, `TESTS`, `BOUNDARY`, `SIZE`

### Cross-Reference Matrix

Show the traceability between PRD ACs, spec sections, and test scenarios:

```
PRD AC  | Spec §              | Test Scenarios      | Status
--------|----------------------|---------------------|--------
AC1     | § 2.1, § 4 (model)  | § 6.1 #7, § 6.2 #7 | COVERED
AC2     | § 3, § 4 (service)  | § 6.1 #1-#6        | COVERED
AC3     | Deferred → F8       | —                   | DEFERRED
AC5     | § 7.2 (F6 consumes) | § 6.1 #8            | COVERED
```

## Tone

Be rigorous and precise. This is a quality gate — its purpose is to catch defects before they propagate into task lists and implementation. Every finding must be actionable. When something is wrong, show exactly what it should say.
