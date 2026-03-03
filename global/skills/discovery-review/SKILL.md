---
name: discovery-review
description: Review a discovery document against Golden Circle quality criteria
argument-hint: <path-to-discovery> (e.g., "DISCOVERY-myproject.md" or leave empty to select)
---

# Discovery Review

Validate a Discovery document against quality standards and report completeness.

**Pipeline position**: `/discovery` (optional) -> **`/discovery-review`** -> `/prd` -> `/prd-review` -> `/feature-spec` -> ...

## Input

Discovery file path from arguments: `$ARGUMENTS`

If no argument is provided, search for `DISCOVERY-*.md` files in the current workspace and ask the user which one to review.

## Checklist

Evaluate the discovery document against each of these criteria. For each item, report **PASS**, **PARTIAL** (present but incomplete), or **MISSING**.

### 1. Clarity of WHY
- [ ] Problem is specific and concrete (not vague or generic)
- [ ] A real audience is identified (not "everyone" or "users")
- [ ] Cost of inaction is explained (urgency or consequence)
- [ ] Focus is on people and outcomes, not technology

### 2. Audience Definition
- [ ] Stakeholders or affected people are named by role or profile
- [ ] Specific enough to guide decisions (could say "this is for them, not for them")
- [ ] More than one audience segment if applicable

### 3. Vision of WHAT
- [ ] One-sentence vision statement is clear and compelling
- [ ] Outcomes are described (what changes), not outputs (what gets built)
- [ ] Scope is delimited — out-of-scope items are explicitly listed

### 4. Strategy of HOW
- [ ] Approach is conceptual and strategic, not technical
- [ ] A core insight or bet is articulated (not just "build an app")
- [ ] Approach connects logically back to the WHY

### 5. Success Criteria
- [ ] At least 3 measurable indicators listed
- [ ] Indicators are traceable to the WHY (solving the stated problem)
- [ ] Indicators are observable and verifiable (not subjective)

### 6. Risks and Constraints
- [ ] At least 2 assumptions documented
- [ ] At least 2 risks identified
- [ ] Constraints acknowledged (budget, timeline, team, regulatory, etc.)

## Output Format

```
Discovery Review -- <filename>
========================================

  1.  Clarity of WHY:       PASS / PARTIAL / MISSING
  2.  Audience Definition:  PASS / PARTIAL / MISSING
  3.  Vision of WHAT:       PASS / PARTIAL / MISSING
  4.  Strategy of HOW:      PASS / PARTIAL / MISSING
  5.  Success Criteria:     PASS / PARTIAL / MISSING
  6.  Risks & Constraints:  PASS / PARTIAL / MISSING
  ----------------------------------------
  Overall:                  X/6 PASS

Findings:
```

After the summary table, for each PARTIAL or MISSING item, provide:
- What specifically is missing or incomplete
- A concrete suggestion for what to add, with example phrasing when helpful

## Tone

Be constructive and specific. The goal is to help the author sharpen the discovery document, not just flag problems. When something is missing, suggest what it should look like. Remember that discovery documents are intentionally concise (50-100 lines) — do not penalize brevity as long as content is substantive.
