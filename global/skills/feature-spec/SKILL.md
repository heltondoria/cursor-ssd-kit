---
name: feature-spec
description: Refine a single PRD feature into a detailed implementation spec for higher-quality task generation
argument-hint: <feature-id> (e.g., "F6" or "F7") — optional PRD path as second arg
---

# Feature Specification Generator

Refine a single PRD feature into a detailed implementation specification. This bridges the gap between the PRD ("what") and task generation ("how"), producing specs that lead to more precise, atomic, and correct task lists.

**Pipeline position**: `/discovery` (optional) -> `/discovery-review` -> `/prd` -> `/prd-review` -> **`/feature-spec`** -> `/feature-to-tasks` -> `/task-review` -> implement

## Input

Feature identifier from arguments: `$ARGUMENTS`

Expected formats:
- `F6` — feature ID only (will search for PRD automatically)
- `F6 PRD-myproject.md` — feature ID + explicit PRD path

If no argument is provided, search for `PRD-*.md` files in the workspace, read the features list, and ask the user which feature to refine.

## Phase 1: Gather Context

### 1.1 Read Reference Documents

Read these files to understand the project:

1. The PRD file — extract the target feature section (description, ACs, endpoints, error scenarios, test strategy) AND § 4 (Business Rules and Shared Requirements) — identify which BRs/SRs the feature references
2. `.cursor/rules/ (project rules)` — project overview, architecture, commands
3. `CONVENTIONS.md` (if exists) — code conventions, patterns, naming

### 1.2 Explore the Codebase (or Establish Foundations)

Use Glob, Grep, and Read tools to explore the existing codebase.

#### For projects WITH existing code:

This is the critical step that differentiates feature-spec from PRD-to-tasks. Answer:

1. **Which files must change?** — Find existing modules that the feature touches. Read their current implementation to understand interfaces.
2. **What patterns exist?** — How does the codebase handle similar operations? What conventions are in use for serialization, storage, error handling, async/sync boundaries?
3. **What conflicts exist?** — Does the feature overlap with existing code? Are there naming conflicts, redundant fields, or incompatible patterns?
4. **What are the integration points?** — Which other features produce data this feature consumes? Which features will consume data this feature produces?

Explore at least:
- Models/types relevant to the feature
- Storage/repository layer (if data persistence is involved)
- Service layer methods the feature will extend
- Router/API endpoints (if HTTP is involved)
- Existing tests (to understand test patterns and fixtures)

#### For GREENFIELD projects (no existing code):

When there is no code to explore, the spec becomes the **founding document** for the feature's architecture. The design decisions section (§ 2.3) is even more critical because you are establishing patterns, not conforming to them.

You must decide and document:
- **Module layout** — Where will this feature's files live? Propose the directory structure.
- **Core abstractions** — What are the base classes, protocols, or interfaces this feature needs?
- **Storage pattern** — Repository pattern? ORM? Direct queries? What's the convention going forward?
- **Error handling pattern** — Exception hierarchy, base class, chaining strategy.
- **Async/sync boundaries** — Which layers are async (I/O) vs sync (computation)?
- **Test patterns** — Fixture strategy, factory functions, test data approach.

Reference the PRD's tech stack and conventions sections when making these foundational choices. Each decision establishes a precedent that other features will follow.

### 1.3 Identify Design Decisions

Based on the codebase exploration (or greenfield analysis), identify decisions that the PRD does NOT cover but that affect implementation:

- Default values (what's backward compatible? what's the right zero-value?)
- Data storage strategy (column vs JSON, indexed vs not?)
- Mutation strategy (load-modify-save vs targeted UPDATE?)
- Async vs sync boundaries
- Feature boundaries (what belongs in THIS feature vs adjacent features?)
- Event-driven concerns (if applicable — see § 9 in template)

## Phase 2: Write the Feature Spec

Generate the spec following the template below. Write it to:

```
.specs/<feature-id>-<feature-slug>.md
```

If a `.specs/` directory doesn't exist, create it.

If the user specifies a different path, use that instead.

### Template

```markdown
# Feature Specification: [FN] — [Feature Name]

> **PRD Reference**: <PRD filename> § <section>, Feature [FN]
> **Status**: Draft
> **Date**: <today>

## 1. Summary

**What**: [one sentence — what the feature does]
**Why**: [one sentence — the user problem this solves]
**PRD ACs**: [list AC IDs]
**Referenced BRs/SRs**: [BR1, BR3, SR2 — IDs from PRD § 4 that this feature must comply with]

---

## 2. Implementation Design

### 2.1 Component Architecture

[List files that will be created or modified, with responsibilities]

```
src/<package>/
  <module>/
    <file>.py    — <responsibility> [NEW | EXISTING — modify]
```

### 2.2 Data Flow

[Input → processing steps → output, including intermediate representations]

### 2.3 Key Design Decisions

[Decisions NOT in the PRD. Each: choice, rationale, rejected alternatives]

| Decision | Choice | Rationale | Alternatives rejected |
|----------|--------|-----------|----------------------|

---

## 3. API Contract

[For each endpoint: request/response JSON schemas with field types]

### `METHOD /api/v1/endpoint`

**Request**:
```json
{"field": "type — description"}
```

**Response (success — NNN)**:
```json
{"field": "value"}
```

**Response (error — NNN)**:
```json
{"detail": "error message"}
```

---

## 4. Internal Interfaces

[Service/repository method signatures with type hints, docstrings, raises.
Each method here becomes a natural TDD boundary: write the test for the
signature first, then implement until the test passes.]

```python
async def method_name(
    self,
    param: ParamType,
) -> ReturnType:
    """Brief description.

    Args:
        param: What this parameter represents.

    Raises:
        SpecificError: When this condition occurs.
    """
    ...
```

---

## 5. Error Scenarios

[Concrete inputs that trigger each error path]

| # | Trigger | Input example | Exception | HTTP | Recovery |
|---|---------|---------------|-----------|------|----------|

---

## 6. Test Scenarios

### Reference Data for Tests

[Shared fixture with named entities and relationships.
All test scenarios below reference this data.]

### 6.1 Happy Path

| # | Scenario | Input | Expected output |
|---|----------|-------|-----------------|

### 6.2 Edge Cases

| # | Scenario | Input | Expected output |
|---|----------|-------|-----------------|

### 6.3 Error Cases

| # | Scenario | Input | Expected exception |
|---|----------|-------|--------------------|

---

## 7. Integration Points

### 7.1 This feature consumes

| Source feature | Interface | Data consumed |
|---------------|-----------|---------------|

### 7.2 Other features consume this

| Consumer feature | Interface | Data provided |
|-----------------|-----------|---------------|

---

## 8. Convention Compliance

### 8.1 Async/Sync

| Operation | Type | Rationale |
|-----------|------|-----------|

### 8.2 Logging Events

| Event | Level | Extra fields |
|-------|-------|-------------|

### 8.3 SQL Migration (if applicable)

[Migration statements]

---

## 9. Async Messaging (if applicable)

[INCLUDE THIS SECTION ONLY if the feature produces or consumes async events.
DELETE it entirely if the feature is purely request/response.

This section defines the event-driven contract for features that communicate
asynchronously — via message brokers, event buses, webhooks, or similar.]

### 9.1 Events Produced

| Event name | Trigger | Schema | Channel/Topic |
|------------|---------|--------|---------------|
| `scope.assigned` | Node scope changes | `ScopeAssignedEvent` | `kaos.graph.events` |

### 9.2 Events Consumed

| Event name | Source | Handler | Idempotency |
|------------|--------|---------|-------------|
| `graph.loaded` | F5 Versioning | `on_graph_loaded()` | By graph_id + version |

### 9.3 Event Schemas

```python
class ScopeAssignedEvent(BaseModel):
    """CloudEvents-compatible envelope."""
    model_config = ConfigDict(frozen=True)

    # CloudEvents metadata
    type: str = "kaos.scope.assigned"
    source: str = "/graphs/{graph_id}"
    id: str = Field(default_factory=lambda: str(uuid4()))
    time: datetime = Field(default_factory=datetime.utcnow)

    # Event payload
    data: ScopeAssignedPayload

class ScopeAssignedPayload(BaseModel):
    graph_id: str
    node_id: str
    scope: str | None
    previous_scope: str | None
```

### 9.4 Delivery Guarantees

| Aspect | Choice | Rationale |
|--------|--------|-----------|
| Delivery | At-least-once | Consumers must be idempotent |
| Ordering | Per-partition (by graph_id) | Events for the same graph are ordered |
| Serialization | JSON (CloudEvents spec) | Human-readable, schema-evolvable |
| Dead letter | Retry 3x, then DLQ | Prevents poison messages from blocking |

### 9.5 Channel Configuration

| Channel/Topic | Partitions | Retention | Consumers |
|---------------|-----------|-----------|-----------|
| `kaos.graph.events` | By graph_id | 7 days | Suggester, TaskExporter |

---
```

## Template Rules

1. **REFERENCE, don't repeat** — If the PRD already specifies something, point to it (e.g., "See PRD § 5, F6 ACs" or "Per BR1 in PRD § 4"). Don't copy ACs or descriptions verbatim.
2. **FOCUS on implementation gaps** — What the PRD doesn't cover: exact method signatures, default values, data shapes, SQL, test data.
3. **TARGET ~300 lines** — Aim for 150-300 lines, but completeness takes priority over brevity. If longer, look for PRD repetition or verbose descriptions to trim — but never cut substantive content to hit a line count.
4. **Every section must add NEW information** not present in the PRD.
5. **Include a reference test dataset** (Section 6) — Named entities with concrete values that all test scenarios reference. This prevents each test from inventing its own setup.
6. **Draw feature boundaries explicitly** (Section 7) — If an AC belongs to another existing feature, reference it. If it doesn't fit any existing feature, propose it as a new feature for the PRD (name + one-line description + which ACs it would cover).
7. **Section 9 is conditional** — Only include it for features that produce or consume async events. When included, define schemas (CloudEvents-compatible), channels, delivery guarantees, and consumer idempotency strategy.
8. **Internal interfaces (Section 4) define TDD boundaries** — Each method signature is a test-first contract. The task generator will use these to pair "write test → implement → test passes" tasks.
9. **Reference BRs/SRs by ID, never copy content** — In § 1, list the BR/SR IDs from PRD § 4. In design decisions and implementation notes, reference by ID (e.g., "Per BR1, all prices use integer cents"). Never copy the BR/SR text — the PRD is the single source of truth.

## Phase 3: Present and Iterate

After writing the spec:

1. Present a brief summary to the user:
   - Component count (new vs modified files)
   - Key design decisions made
   - Feature boundary choices
   - Test scenario count (happy path / edge case / error)
   - Async messaging: events produced/consumed (if applicable)

2. Ask if they want to review or adjust any decisions before proceeding to task generation.

## Output

The primary output is the feature spec file. The user then runs:
- `/feature-to-tasks` with the spec as input for TDD-structured task generation

## Tone

Be precise and analytical. The spec is a technical contract — every statement should be verifiable against the codebase. When making design decisions, always explain the rationale and what alternatives were rejected.

## Commit

Commit the generated feature spec:
- Type: `docs`
- Scope: feature ID (e.g., `F6`)
- Example: `docs(F6): generate feature spec for <feature-slug>`
