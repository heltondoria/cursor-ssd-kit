---
name: prd-import
description: Import an external PRD into the SDD format without content loss
argument-hint: <path-to-external-prd>
---

# PRD Import

Import an external PRD (any format) into the standard SDD format. Preserves all original content, reorganizing it into the 12 sections expected by the pipeline.

**Pipeline position**: alternative entry point — replaces `/prd` when an external PRD already exists.
```
PRD externo  ->  /prd-import  ->  /prd-review  ->  /feature-spec  ->  ...
```

---

## Input

Parse `$ARGUMENTS`:
- Path to the external PRD file (required)
- If not provided, ask the user for the path

Also read (if they exist):
- `CONVENTIONS.md` — to adapt code examples to the project's style
- `pyproject.toml` or `package.json` — to detect the stack and adapt examples

---

## Phase 1: Ingestion and Analysis

1. **Read the entire external PRD** — regardless of size
2. **Inventory the content** — list each section/block of the original document with:
   - Original title/heading
   - Content summary (1-2 lines)
   - Target SDD section (which of the 12 sections will receive this content)
   - Flag: `direct` (maps 1:1), `split` (content goes to >1 section), `enrich` (target section needs supplementation)
3. **Identify gaps** — SDD format sections that have no corresponding content in the original PRD:
   - Mark as `MISSING` — needs to be generated or asked from the user
4. **Identify extra content** — blocks from the original PRD that don't map to any of the 12 sections:
   - Will be included as Appendix in the final PRD

Show the inventory to the user in table format:

```
Content Map
===========
Source Section                    -> Target SDD Section              Status
---------------------------------------------------------------------------
"1. Introduction"                 -> 1. Overview                     direct
(no source)                       -> 2. Business Context             MISSING
"2. Market Analysis"              -> 3. Target Audience              split (also -> 11)
(no source)                       -> 4. Business Rules & Shared Reqs MISSING
"3. Requirements"                 -> 5. Core Features                direct
"Technical Architecture"          -> 6. Tech Stack                   direct
"Database Design"                 -> 7. Data Model                   direct
(no source)                       -> 8. UI Design                    MISSING
"Auth & Permissions"              -> 9. Security                     direct
"Roadmap"                         -> 10. Implementation Phases       direct
(no source)                       -> 11. Challenges                  MISSING
"Vision & Future"                 -> 12. Future Expansion            direct
"Compliance Notes"                -> Appendix                        extra
```

Ask the user for confirmation: **"Does this mapping look correct? Any adjustments?"**

---

## Phase 2: Feature Extraction

This phase is critical — the SDD pipeline depends on enumerated features (F1, F2, ...) with acceptance criteria.

1. **Identify features** in the original PRD — they may appear as:
   - Numbered sections ("Feature 1: ...", "Requirement 3.1: ...")
   - User stories ("As a user, I want to...")
   - Descriptive bullet lists
   - Requirements tables
   - Mixed across multiple sections

2. **Enumerate features** in SDD format: `F1`, `F2`, ..., `F{N}`

3. **For each feature, extract or derive**:
   - Short name (slug)
   - Description
   - Acceptance criteria (if they exist in the original, preserve verbatim; if not, derive from content)
   - Priority (must-have vs nice-to-have) — if not explicit, ask the user

4. **Extract or derive Business Rules and Shared Requirements** — look for:
   - Explicit business rules ("must", "shall", "always", "never" statements that span features)
   - Regulatory/compliance references
   - Cross-cutting technical constraints
   - Assign IDs: BR1, BR2... for business rules; SR1, SR2... for shared requirements
   - Map each to the features it applies to

Show to user and ask for confirmation.

5. Show the feature list to the user:

```
Extracted Features
==================
F1: user-authentication - Sign up, login, password reset (must-have)
    ACs: 4 extracted from original
F2: dashboard - Main dashboard with metrics overview (must-have)
    ACs: 2 extracted, 1 derived
F3: export-reports - Export data in CSV/PDF (nice-to-have)
    ACs: 3 derived (original had no explicit ACs)
...
```

Ask for confirmation and adjustments.

---

## Phase 3: Conversion

Generate the PRD in SDD format with the 12 mandatory sections:

```markdown
# PRD: [Project Name]

## 1. App Overview and Objectives
## 2. Business Context
## 3. Target Audience
## 4. Business Rules and Shared Requirements
## 5. Core Features and Functionality
## 6. Technical Stack Recommendations
## 7. Conceptual Data Model
## 8. UI Design Principles
## 9. Security Considerations
## 10. Implementation Phases
## 11. Potential Challenges and Solutions
## 12. Future Expansion Possibilities
```

### Conversion rules

1. **Preserve original content** — never invent information that is not in the source PRD. If a section is MISSING, include a clear placeholder:
   ```markdown
   ## 6. UI Design Principles
   > **TODO**: This section was not present in the original PRD. Fill in before running `/prd-review`.
   ```

2. **Adapt code examples** (if they exist) to the project's style:
   - Python: modern type hints (`list[T]`, `X | None`), Google docstrings, structured logging
   - TypeScript: strict types, Biome formatting

3. **Features in section 5** must follow the format:
   ```markdown
   ### F1: Feature Name
   Description...

   **Acceptance Criteria:**
   - AC1: ...
   - AC2: ...
   ```

4. **Section 10 (Implementation Phases)** must list features in implementation order respecting dependencies between them.

5. **Extra content** (that doesn't fit any section) goes to an Appendix at the end:
   ```markdown
   ## Appendix: Additional Context (from original PRD)
   ### [Original Section Title]
   [Content preserved as-is]
   ```

---

## Phase 4: Validation

1. Mentally run the 13 criteria from `/prd-review` on the generated PRD
2. For each criterion, report status: PASS, PARTIAL, MISSING
3. Show summary to the user:

```
Pre-validation (prd-review criteria)
=====================================
 1. Overview Section          PASS
 2. Target Audience           PASS
 3. Core Features             PASS
 4. API Surface               PARTIAL - no code examples in original
 5. Data Model                PASS
 6. Error Handling            MISSING - not in original PRD
 7. Test Strategy             MISSING - not in original PRD
 8. Dependencies              PASS
 9. Non-Functional Reqs       PASS
10. Development Phases        PASS
11. Convention Compliance     PARTIAL - code examples need adaptation
12. Business Context          PARTIAL - domain identified, glossary missing
13. Business Rules & SRs      PASS - 3 BRs, 2 SRs extracted

Recommendation: Run `/prd-review` after filling TODOs in sections 6, 7.
```

---

## Output

Save the converted PRD as: `PRD-[ProjectName].md` in the workspace root.

```
PRD Import Complete
===================
Source:       docs/external-prd.md (2130 lines)
Output:       PRD-MyProject.md (850 lines)
Features:     12 features extracted (F1-F12)
BRs/SRs:      3 BRs, 2 SRs extracted
Sections:     10/12 complete, 2 with TODOs
Appendix:     2 sections preserved from original

Next steps:
  - Fill TODO sections
  - Run `/prd-review` to validate completeness
  - Then continue pipeline: `/feature-spec F1`
```

---

## Reminders

- NEVER invent content — if the info doesn't exist in the original, mark as TODO
- Preserve EVERYTHING — no information from the original PRD should be lost
- Features MUST have IDs (F1, F2, ...) — the entire pipeline depends on this
- If the original PRD is very large, process in chunks but maintain coherence
- Content that doesn't fit any section goes to Appendix, never discarded
- If the original PRD already has acceptance criteria, preserve them verbatim
- Adapt code examples to the detected stack (Python/TypeScript) and project conventions
- Business Rules use IDs BR1, BR2, ...; Shared Requirements use IDs SR1, SR2, ...
- Each BR/SR MUST have an "Applies to" column mapping to feature IDs (F1, F2, ...)
- Features in § 5 MUST include a "Referenced BRs/SRs" line listing applicable IDs

---

## Commit

```
docs(prd): import PRD for <project-name> from external format
```
