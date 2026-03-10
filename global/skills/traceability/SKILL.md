---
name: traceability
description: Analyze BR/SR cross-references between PRD and feature specs to detect dangling references, orphans, and staleness
argument-hint: [Optional path-to-prd] (defaults to auto-detect PRD-*.md)
---

# BR/SR Traceability Analysis

Analyze cross-references between Business Rules (BRs) / Shared Requirements (SRs) in the PRD and their usage in feature specs. Detects dangling references, orphans, coverage gaps, and potentially stale specs.

**Pipeline position**: `/prd` -> `/prd-review` -> `/feature-spec` (x N) -> **`/traceability`** (optional) -> `/feature-review` -> `/feature-to-tasks` -> ...

This is a **read-only analysis skill** — it does not modify any files.

## Input

Parse `$ARGUMENTS`:
- Optional path to the PRD file
- If not provided, search for `PRD-*.md` files in the workspace root

Also locate all feature spec files: `.specs/*.md`

If no PRD or no specs are found, report the issue and exit.

---

## Phase 1: Extract BRs/SRs from PRD

Read the PRD and parse § 4 (Business Rules and Shared Requirements).

For each BR and SR, extract:
- **ID**: BR1, BR2, ..., SR1, SR2, ...
- **Description**: The rule or requirement text
- **Applies to**: List of feature IDs (F1, F2, ...) or "All features"

Build a registry:

```
PRD BR/SR Registry
==================
ID   | Description                                      | Applies to
-----|--------------------------------------------------|------------
BR1  | All monetary values stored as integer cents       | F1, F3
BR2  | Users cannot delete their own account while subscribed | F2, F5
SR1  | All write endpoints require authentication        | All features
SR2  | Audit log every state change                      | F1, F2, F4
```

If § 4 does not exist or contains no BRs/SRs, report:
```
No Business Rules or Shared Requirements found in PRD § 4.
Consider adding them — run `/prd` or edit the PRD directly.
```
And exit.

---

## Phase 2: Extract References from Feature Specs

For each `.specs/*.md` file:

1. **Extract feature ID** from the filename or header (e.g., `F6` from `F6-billing.md`)
2. **Extract referenced BRs/SRs** — scan for BR/SR IDs in:
   - § 1 "Referenced BRs/SRs" line
   - Inline references in text (e.g., "Per BR1, ...", "BR1 applies here")
   - Tables mentioning BR/SR IDs
3. **Extract last modified date** — use `git log -1 --format=%ci -- <filepath>` (best-effort; skip if not a git repo)

Build a spec reference list:

```
Feature Spec References
=======================
Spec File                        | Feature | Referenced BRs/SRs | Last Modified
---------------------------------|---------|--------------------|--------------
.specs/F1-user-auth.md           | F1      | BR1, SR1, SR2      | 2026-03-01
.specs/F2-subscriptions.md       | F2      | BR2, SR1, SR2      | 2026-03-02
.specs/F3-billing.md             | F3      | BR1, SR1           | 2026-02-28
```

---

## Phase 3: Build Traceability Matrix

Cross-reference the PRD registry (Phase 1) with spec references (Phase 2).

```
Traceability Matrix
====================
BR/SR | PRD "Applies to"   | Specs that reference | Status
------|--------------------|-----------------------|--------
BR1   | F1, F3             | F1, F3                | COVERED
BR2   | F2, F5             | F2                    | GAP (F5 missing)
SR1   | All features       | F1, F2, F3            | COVERED
SR2   | F1, F2, F4         | F1, F2                | GAP (F4 missing)
```

---

## Phase 4: Detect Issues

Scan for 4 types of issues:

### 4.1 Dangling References (HIGH)

A feature spec references a BR/SR ID that **does not exist** in the PRD § 4.

```
DANGLING REFERENCES (HIGH)
===========================
Spec                    | References | Issue
------------------------|------------|------
.specs/F3-billing.md    | BR9        | BR9 does not exist in PRD § 4
.specs/F5-reports.md    | SR5        | SR5 does not exist in PRD § 4
```

### 4.2 Orphan BRs/SRs (MEDIUM)

A BR/SR exists in the PRD § 4 but **no feature spec references it**.

```
ORPHAN BRs/SRs (MEDIUM)
========================
ID   | Description                              | Applies to | Issue
-----|------------------------------------------|------------|------
BR4  | All dates stored as UTC ISO 8601         | F2, F6     | No spec references BR4
```

### 4.3 Coverage Gaps (MEDIUM)

The PRD says a BR/SR "applies to" a feature, but that feature's spec **does not reference it**.

```
COVERAGE GAPS (MEDIUM)
======================
BR/SR | PRD says applies to | Missing from spec
------|--------------------|-----------
BR2   | F2, F5             | F5
SR2   | F1, F2, F4         | F4
```

### 4.4 Potentially Stale Specs (LOW)

A feature spec was last modified **before** the PRD was last modified. This may indicate the spec is outdated (the PRD may have changed BRs/SRs after the spec was written).

```
POTENTIALLY STALE SPECS (LOW)
=============================
Spec                    | Spec modified | PRD modified | Delta
------------------------|---------------|--------------|------
.specs/F3-billing.md    | 2026-02-28    | 2026-03-05   | 5 days behind
```

Note: This check is best-effort. If git is not available, skip this section entirely.

---

## Output

### Summary

```
BR/SR Traceability Report
=========================
PRD:          PRD-MyProject.md
Specs:        5 feature specs analyzed
BRs:          4 business rules in PRD
SRs:          3 shared requirements in PRD

Issues Found:
  HIGH   - Dangling references:    0
  MEDIUM - Orphan BRs/SRs:         1
  MEDIUM - Coverage gaps:          2
  LOW    - Potentially stale:      1

Result: 4 issues found
```

If no issues: `Result: CLEAN`

---

## Rules

1. **Read-only** — This skill does not modify any files. It only reads and reports.
2. **No Commit section** — This is an analysis skill; no artifacts are produced.
3. **Generous scanning** — BRs/SRs may appear in tables, inline text, headers, or bullet points. Scan broadly.
4. **Git dates are best-effort** — If the workspace is not a git repository, skip the staleness check (Phase 4.4) and note it in the output.
5. **"All features" handling** — When a BR/SR says "Applies to: All features", every feature spec should reference it. Check all specs.
6. **Case-insensitive matching** — Match BR1, br1, Br1 as the same ID.
