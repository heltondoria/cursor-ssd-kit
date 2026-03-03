---
name: prd-review
description: Review a PRD against the project quality checklist and conventions
argument-hint: <path-to-prd> (e.g., "PRD-myproject.md" or leave empty to select)
---

# PRD Review

Validate a Product Requirements Document against quality standards and report completeness.

## Input

PRD file path from arguments: `$ARGUMENTS`

If no argument is provided, search for `PRD-*.md` files in the current workspace and ask the user which one to review.

## Reference Documents

Before reviewing, read these files to understand the project context:

1. `.cursor/rules/ (project rules)` from workspace root — project overview and architecture
2. `CONVENTIONS.md` from workspace root (if exists) — code conventions that PRD examples must follow

## Checklist

Evaluate the PRD against each of these criteria. For each item, report **PASS**, **PARTIAL** (present but incomplete), or **MISSING**.

### 1. Overview Section
- [ ] Project name and one-line description
- [ ] Problem statement clearly defined
- [ ] Key objectives and success metrics
- [ ] Status marker present (Planned, Active, Implemented)

### 2. Target Audience
- [ ] Primary users identified
- [ ] User needs and pain points described
- [ ] User personas or profiles (at least brief)

### 3. Core Features
- [ ] Feature list with clear enumeration
- [ ] Each feature has enough detail to implement
- [ ] Acceptance criteria defined for each feature
- [ ] Features prioritized (must-have vs nice-to-have)

### 4. API Surface / Public Interface
- [ ] Public API documented with code examples
- [ ] Import statements included in examples
- [ ] Examples follow project conventions (type hints, docstrings)
- [ ] Configuration examples included

### 5. Data Model
- [ ] Entities with fields, types, and relationships
- [ ] Validation rules defined
- [ ] Pydantic models use `frozen=True` (if applicable)

### 6. Error Handling Strategy
- [ ] Exception hierarchy defined (project base exception + sub-exceptions)
- [ ] Error scenarios documented for each feature
- [ ] Exception chaining with `from e` shown in examples

### 7. Test Strategy
- [ ] Coverage target specified (should be 100% for Python, 90%+ for TS)
- [ ] Key test scenarios listed per feature
- [ ] Test naming follows convention
- [ ] Integration test strategy described (if applicable)

### 8. Dependencies
- [ ] All runtime dependencies listed with version constraints
- [ ] Internal project dependencies documented
- [ ] Optional dependency groups defined (if applicable)

### 9. Non-Functional Requirements
- [ ] Performance considerations documented
- [ ] Security considerations documented
- [ ] Scalability considerations (if applicable)

### 10. Development Phases
- [ ] Implementation phases defined
- [ ] Phase ordering makes sense (dependencies respected)
- [ ] Each phase is achievable incrementally

### 11. Convention Compliance
- [ ] All code examples follow `CONVENTIONS.md` patterns
- [ ] Structured logging uses correct patterns (no f-strings in log messages)
- [ ] Import order follows project conventions
- [ ] Async/sync decisions explicit

## Output Format

```
PRD Review -- <PRD filename>
========================================

  1.  Overview:              PASS / PARTIAL / MISSING
  2.  Target Audience:       PASS / PARTIAL / MISSING
  3.  Core Features:         PASS / PARTIAL / MISSING
  4.  API Surface:           PASS / PARTIAL / MISSING
  5.  Data Model:            PASS / PARTIAL / MISSING
  6.  Error Handling:        PASS / PARTIAL / MISSING
  7.  Test Strategy:         PASS / PARTIAL / MISSING
  8.  Dependencies:          PASS / PARTIAL / MISSING
  9.  Non-Functional:        PASS / PARTIAL / MISSING
 10.  Development Phases:    PASS / PARTIAL / MISSING
 11.  Convention Compliance: PASS / PARTIAL / MISSING
  ----------------------------------------
  Overall:                   X/11 PASS

Findings:
```

After the summary table, for each PARTIAL or MISSING item, provide:
- What specifically is missing or incomplete
- A concrete suggestion for what to add (with example text/code when helpful)

## Tone

Be constructive and specific. The goal is to help the author improve the PRD, not just flag problems. When something is missing, suggest what it should look like.
