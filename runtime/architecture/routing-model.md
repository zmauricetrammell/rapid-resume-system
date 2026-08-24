# RRS V3 Routing Model

## Status

Draft V0.7 — FIX-003, FIX-004, FIX-007, FIX-020, FIX-021, and FIX-031 applied

## Purpose

The Routing Model defines how the V3 runtime derives lifecycle transitions from committed professional artifact state.

The router does not perform professional reasoning.

It evaluates deterministic predicates over current, schema-defined professional state and selects the next Runtime Job lifecycle phase.

Routing is a control-plane responsibility.

Professional agents remain unaware of routing, Trello, Discord, other agents, downstream consumers, and workflow position.

---

# Core Invariants

1. Routing evaluates only committed current professional state.
2. Routing never acts on raw, staged, schema-invalid, stale, or partially committed output.
3. Routing uses deterministic predicates.
4. Routing prefers schema-defined fields over free-form prose.
5. Professional interpretation remains inside V2 agents.
6. Evidence Uncertainty outranks Product Defect when both are blocking.
7. Candidate Limitations never directly create lifecycle transitions.
8. Evidence Request resolution is determined through Researcher re-analysis, not merely by receipt of an Evidence Response.
9. Routing decisions are append-only Runtime Job history.
10. Routing decisions describe state transitions, not agent assignments.
11. Self-transitions are allowed when a phase still contains incomplete runtime work.
12. Terminal lifecycle states do not route automatically.
13. A routing-history append and lifecycle transition are one authoritative Runtime Job mutation and commit atomically with the resulting `lifecycle_changed` Event.
14. `artifact_committed` is the sole canonical professional-state routing trigger; Execution completion alone never triggers routing.
15. Routine no-change routing evaluations do not append routing history; self-transitions are recorded only when they represent a discrete meaningful work milestone.
16. V0.1 routing does not infer or route on deferred Information Request, Information Response, or Target Role state; those concepts await the Analyst/Custodian architecture.

---

# 1. Router Inputs

The router consumes:

```text
Runtime Job
+
current committed professional artifact pointers
```

It may resolve exact current artifact contents needed by a predicate.

Examples:

```text
current JEA
current active ERQs
current unintegrated Evidence Responses
current Resume
current WCM
current Resume Evaluation
```

The router must not consume arbitrary historical artifacts unless the predicate explicitly requires them.

---

# 2. Router Output

A routing decision contains:

```yaml
decision_id: ROUTE-00017
decided_at: datetime

from_phase: analysis
to_phase: evidence_request

predicate:
  name: has_unresolved_material_evidence_needs
  result: true

basis:
  - artifact_type: job_experience_analysis
    artifact_id: JEA-0004
    artifact_version: 3

reason: "Two unresolved Material Evidence Needs remain."

execution_id: EXEC-0042
```

When the transition is valid, the routing decision is applied as one atomic Runtime Job mutation:

```text
append Runtime Job.routing_history
+
update Runtime Job.lifecycle.phase
+
update Runtime Job.lifecycle.entered_at
+
increment Runtime Job revision
+
persist lifecycle_changed Event
```

These changes must commit together in one SQLite transaction.

The router must not append routing history separately from the lifecycle transition.

---

# 3. Routing Decision Boundary

A routing decision answers:

> Given current committed professional state, what lifecycle phase should the Runtime Job enter?

It does **not** answer:

- Which agent should receive work.
- Who owns a deficiency.
- Who should investigate.
- What professional conclusion should be reached.
- What content should be written.
- What interview question should be asked.

Example:

```text
analysis → evidence_request
```

not:

```text
Researcher → Interviewer
```

---

# 4. Predicate Vocabulary

V0.1 defines the following core predicates:

```text
has_unresolved_material_evidence_needs

has_missing_active_erqs

has_active_erqs

has_erqs_awaiting_evidence_response

has_unintegrated_evidence_responses

has_blocking_product_defects

has_blocking_evidence_uncertainties

is_ready_to_submit
```

Additional predicates should be introduced only when required behavior cannot be expressed with this set.

---

# 5. Predicate: has_unresolved_material_evidence_needs

## Purpose

Determine whether the current Job Experience Analysis identifies factual issues that remain materially worth human investigation.

## Input

Current committed JEA.

## Evaluation

Return `true` when one or more Material Evidence Needs have a status that remains unresolved and materially investigable.

Expected unresolved states:

```text
open
partially_resolved
```

Expected non-routing states:

```text
resolved
no_longer_material
```

Exact enum values must follow the authoritative JEA schema.

## Rule

Do not infer evidence need from narrative prose.

Use schema-defined Material Evidence Need state.

---

# 6. Predicate: has_missing_active_erqs

## Purpose

Determine whether every currently unresolved Material Evidence Need has a corresponding current Evidence Request.

## Inputs

- Current committed JEA.
- Runtime Job `active_erqs`.

## Evaluation

Return `true` when at least one unresolved Material Evidence Need lacks an active Evidence Request representing that current need.

The association must be derived from schema-defined ERQ origin/target context rather than free-text similarity.

## Why This Exists

Analysis and Evidence Request generation are separate professional operations.

Example:

```text
JEA:
EN-001 open
EN-002 open
EN-003 open

active_erqs:
ERQ for EN-001
ERQ for EN-002
```

Result:

```text
has_missing_active_erqs = true
```

The Runtime Job remains in:

```text
evidence_request
```

until required ERQs exist.

---

# 7. ERQ State Predicates

## Predicate: has_active_erqs

### Purpose

Determine whether current Evidence Requests remain part of the active evidence-resolution loop.

### Input

Runtime Job:

```text
professional_state.active_erqs
```

### Evaluation

Return `true` when one or more current ERQ references remain in `active_erqs`.

Return `false` when `active_erqs` is empty.

Receipt of an Evidence Response does not automatically remove an ERQ from the active evidence-resolution loop.

An ERQ remains active until Researcher re-analysis determines that its underlying Material Evidence Need is:

```text
resolved
```

or:

```text
no_longer_material
```

If re-analysis determines the need remains material, the ERQ remains active or may be superseded by a newer ERQ version according to professional artifact semantics.

## Predicate: has_erqs_awaiting_evidence_response

### Purpose

Determine whether any current active Evidence Request lacks a corresponding committed current Evidence Response.

### Inputs

- Runtime Job `active_erqs`.
- Current committed Evidence Responses associated with those ERQs.

### Evaluation

Return `true` when at least one current active ERQ lacks a committed current Evidence Response for that exact ERQ version.

Return `false` when every current active ERQ has a corresponding committed current Evidence Response.

The association must use schema-defined ERQ/Evidence Response identity or provenance fields rather than free-text similarity.

### Distinction

```text
has_active_erqs
= ERQs still participating in the evidence-resolution loop

has_erqs_awaiting_evidence_response
= active ERQs still requiring committed investigation output
```

These predicates are not interchangeable.

---

# 8. Predicate: has_unintegrated_evidence_responses

## Purpose

Determine whether Evidence Responses exist that have not yet been reconciled into authoritative professional evidence.

## Input

Runtime Job:

```text
professional_state.unintegrated_evidence_responses
```

## Evaluation

```text
list contains one or more current references
→ true

list empty
→ false
```

No professional interpretation is required.

---

# 9. Predicate: has_blocking_product_defects

## Purpose

Determine whether the current Resume Evaluation contains any Product Defect that blocks submission.

## Input

Current committed Resume Evaluation.

## Evaluation

Return `true` when a finding satisfies:

```text
finding_class == product_defect
AND
blocks_submission == true
```

Where possible, validate membership against:

```text
blocking_finding_ids
```

The router should use authoritative schema fields rather than narrative severity descriptions.

---

# 10. Predicate: has_blocking_evidence_uncertainties

## Purpose

Determine whether the current Resume Evaluation contains unresolved factual uncertainty that blocks submission.

## Input

Current committed Resume Evaluation.

## Evaluation

Return `true` when a finding satisfies:

```text
finding_class == evidence_uncertainty
AND
blocks_submission == true
```

Evidence Uncertainty has higher routing priority than Product Defect.

---

# 11. Predicate: is_ready_to_submit

## Purpose

Determine whether the current Resume Evaluation explicitly establishes product readiness.

## Input

Current committed Resume Evaluation.

## Evaluation

Expected condition:

```text
submission_readiness.state == ready_to_submit
AND
blocking_finding_ids == []
```

Candidate Limitations do not invalidate this predicate.

The router must not infer readiness independently from overall fit score.

---

# 12. Candidate Limitations

Candidate Limitations are deliberately excluded from routing predicates.

They may affect:

- Fit assessment.
- ATS risk.
- Recruiter risk.
- Hiring-manager risk.
- Human application strategy.

They do not directly create:

- Re-analysis.
- Evidence Request.
- Resume rewrite.
- Investigation.
- Infinite revision loops.

Example:

```text
Brooks requires ITIL 4
Candidate truthfully holds ITIL v5
No factual uncertainty remains
```

Runtime behavior:

```text
Candidate Limitation recorded
+
no blocking findings
+
ready_to_submit
→ complete
```

---

# 13. Normal Lifecycle Transition Table

| Current Phase | Condition | Next Phase |
|---|---|---|
| `new` | Runtime Job initialized and required starting inputs available | `analysis` |
| `analysis` | `has_unresolved_material_evidence_needs == true` | `evidence_request` |
| `analysis` | `has_unresolved_material_evidence_needs == false` | `resume_production` |
| `evidence_request` | `has_missing_active_erqs == true` | `evidence_request` |
| `evidence_request` | `has_missing_active_erqs == false` and active ERQs exist | `investigation` |
| `investigation` | `has_erqs_awaiting_evidence_response == true` | `investigation` |
| `investigation` | `has_erqs_awaiting_evidence_response == false` and `has_unintegrated_evidence_responses == true` | `evidence_integration` |
| `evidence_integration` | `has_unintegrated_evidence_responses == true` | `evidence_integration` |
| `evidence_integration` | `has_unintegrated_evidence_responses == false` | `analysis` |
| `resume_production` | current Resume + WCM pair committed | `evaluation` |
| `evaluation` | `has_blocking_evidence_uncertainties == true` | `analysis` |
| `evaluation` | no blocking Evidence Uncertainty and `has_blocking_product_defects == true` | `resume_production` |
| `evaluation` | `is_ready_to_submit == true` | `complete` |

---

# 14. Analysis Routing

After successful `generate_analysis` commit:

```text
current phase: analysis
        │
        ▼
has_unresolved_material_evidence_needs?
        │
   ┌────┴────┐
   │         │
  true      false
   │         │
   ▼         ▼
evidence_   resume_
request     production
```

No additional professional interpretation is performed by the router.

---

# 15. Evidence Request Routing

Upon entering:

```text
evidence_request
```

the runtime evaluates:

```text
has_missing_active_erqs
```

If true:

```text
remain evidence_request
```

and required Evidence Request operations may be scheduled.

If false and active ERQs exist:

```text
evidence_request
→ investigation
```

The router does not create ERQs itself.

Handlers invoke the professional `request_evidence` operation.

---

# 16. Multiple Material Evidence Needs

Material Evidence Needs may fan out into multiple Evidence Request operations.

Example:

```text
JEA
├── EN-001
├── EN-002
└── EN-003
```

Runtime state:

```text
evidence_request
```

Professional operations:

```text
EN-001 → ERQ-0011
EN-002 → ERQ-0012
EN-003 → ERQ-0013
```

The Job remains in:

```text
evidence_request
```

until:

```text
has_missing_active_erqs == false
```

Then:

```text
investigation
```

---

# 17. Investigation Routing

The investigation lifecycle phase represents human factual investigation over current active ERQs.

Conceptually:

```text
active ERQs
     │
     ▼
human investigation
     │
     ▼
Evidence Responses
```

The Job remains in:

```text
investigation
```

while `has_erqs_awaiting_evidence_response == true`.

The Job may leave `investigation` only when every current active ERQ has a committed current Evidence Response.

Required condition:

```text
has_erqs_awaiting_evidence_response == false
AND
has_unintegrated_evidence_responses == true
```

Then:

```text
investigation
→ evidence_integration
```

The existence of one or more unintegrated Evidence Responses is not sufficient while another active ERQ still awaits its Evidence Response.

---

# 18. ERQ Resolution Rule

Evidence Response creation does **not** equal Evidence Request resolution.

Example:

```text
ERQ-0011
      ↓
ERESP-0008
```

The Evidence Response may establish:

- Full support.
- Partial support.
- Negative evidence.
- Contradiction.
- Remaining uncertainty.

Only Researcher professional reconciliation and subsequent re-analysis determines whether the underlying Material Evidence Need remains material.

Therefore:

```text
ERQ stays active
until re-analysis determines
need == resolved or no_longer_material
```

This preserves Researcher authority.

---

# 19. Evidence Integration Routing

Upon entering:

```text
evidence_integration
```

the runtime processes:

```text
unintegrated_evidence_responses
```

While any remain:

```text
stay evidence_integration
```

After all are successfully reconciled and current JER pointers commit:

```text
has_unintegrated_evidence_responses == false
```

then:

```text
evidence_integration
→ analysis
```

Re-analysis is mandatory.

The runtime must not route directly from evidence integration to resume production.

---

# 20. Re-Analysis Rule

All newly integrated evidence returns through:

```text
analysis
```

The same original routing predicate applies again:

```text
has_unresolved_material_evidence_needs
```

This avoids special-case routing for revised evidence.

Example:

```text
Evidence integrated
      ↓
Analysis
      ↓
Need resolved?
  ┌───┴───┐
 yes      no
  │        │
  ▼        ▼
resume   evidence
        request loop
```

---

# 21. Active ERQ Cleanup

After re-analysis:

If a Material Evidence Need is:

```text
resolved
```

or:

```text
no_longer_material
```

the runtime may remove the corresponding ERQ from:

```text
professional_state.active_erqs
```

The ERQ artifact itself remains immutable in artifact history.

If the need remains:

```text
open
```

or:

```text
partially_resolved
```

the ERQ remains active or may be superseded according to ERQ version semantics.

---

# 22. Resume Production Routing

The Runtime Job enters:

```text
resume_production
```

only when current analysis contains no unresolved Material Evidence Needs requiring investigation.

The Writer operation must commit the coupled:

```text
Targeted Resume
+
Writer Content Manifest
```

Only after both become current may the Job transition:

```text
resume_production
→ evaluation
```

---

# 23. Evaluation Routing Priority

Evaluation routing uses strict priority:

```text
1. Blocking Evidence Uncertainty
2. Blocking Product Defect
3. Ready to Submit
```

This prevents unnecessary rewriting against unresolved professional state.

---

# 24. Evaluation: Blocking Evidence Uncertainty

Condition:

```text
has_blocking_evidence_uncertainties == true
```

Transition:

```text
evaluation
→ analysis
```

Reason:

Researcher must independently reconcile the factual condition against authoritative professional evidence before another resume is generated.

The router does not assume that investigation is required.

Possible professional outcomes after re-analysis:

```text
existing evidence resolves concern
→ resume_production

material unresolved factual need
→ evidence_request

known absence
→ Candidate Limitation
→ resume_production when no Material Evidence Needs remain
```

---

# 25. Evaluation: Blocking Product Defect

Condition:

```text
has_blocking_evidence_uncertainties == false
AND
has_blocking_product_defects == true
```

Transition:

```text
evaluation
→ resume_production
```

The Writer may consume the current Resume Evaluation as authorized product feedback.

The router does not identify Writer as corrective owner.

It only derives the professional lifecycle state:

```text
resume_production
```

---

# 26. Evaluation: Ready to Submit

Condition:

```text
has_blocking_evidence_uncertainties == false

AND

has_blocking_product_defects == false

AND

is_ready_to_submit == true
```

Transition:

```text
evaluation
→ complete
```

Candidate Limitations may still exist.

They do not prevent completion.

---

# 27. Inconsistent Evaluation State

Example:

```text
submission_readiness == ready_to_submit
BUT
blocking_finding_ids is not empty
```

This is internally inconsistent professional state.

The router must not guess which field is correct.

Recommended behavior:

```text
health.status → blocked
lifecycle.phase → manual_review
```

The inconsistency should also be logged as runtime validation failure.

Schema constraints should prevent this when practical, but routing must fail safely if inconsistent state reaches runtime.

---

# 28. Evaluation With Both Blocking Classes

Example:

```text
Blocking Product Defect
+
Blocking Evidence Uncertainty
```

Transition:

```text
evaluation
→ analysis
```

Evidence Uncertainty wins.

Reason:

Professional state should be resolved before presentation is regenerated.

The later JEA and resume-generation cycle can incorporate both the clarified evidence state and prior product feedback.

---

# 29. Nonblocking Findings

Nonblocking Product Defects and Evidence Uncertainties do not independently route.

Example:

```text
Product Defect
blocks_submission: false
```

or:

```text
Evidence Uncertainty
blocks_submission: false
```

If:

```text
submission_readiness == ready_to_submit
AND
blocking_finding_ids == []
```

the Job may complete.

This preserves the V2 definition:

> Ready means strongest truthful product reasonably available, not perfect candidate/product state.

---

# 30. Self-Transitions and No-Change Evaluations

Routing predicates may determine that the Runtime Job should remain in its current lifecycle phase.

Examples:

```text
evidence_request
→ evidence_request
```

because some Material Evidence Needs still lack ERQs.

```text
investigation
→ investigation
```

because one or more active ERQs still await Evidence Responses.

```text
evidence_integration
→ evidence_integration
```

because unintegrated Evidence Responses remain.

A routine no-change evaluation is not itself a routing decision worth preserving in history.

Canonical rule:

```text
predicate evaluation produces no lifecycle phase change
AND
no discrete meaningful work milestone occurred
→ do not append routing_history
```

A self-transition may be recorded only when it represents a discrete completed runtime milestone that is useful for audit.

Example:

```text
ERQ-0011 committed
Job remains evidence_request because EN-002 still lacks an ERQ
```

If runtime policy considers that milestone worth recording, one deliberate self-transition may be appended.

Do not append repeated self-transitions for polling, retries, wake-ups, or identical unchanged state.

The default V0.1 behavior is:

```text
no lifecycle phase change
→ no routing_history entry
```

unless the caller explicitly identifies a meaningful milestone.

---

# 30.1 Deferred Analyst / Custodian Routing State

V0.1 routing is intentionally limited to the current V2-compatible professional artifact flow.

The following future concepts are explicitly deferred:

```text
Target Role
Information Request
Information Response
```

The router must not infer their existence from prose, agent commentary, or missing evidence.

V0.1 therefore defines no predicates such as:

```text
target_role exists
information_request pending
information_response available
```

and no lifecycle transitions dedicated to those concepts.

The future Analyst/Custodian design may introduce a flow such as:

```text
target analysis
→ information request
→ evidence retrieval/custody
→ information response
→ analysis
```

but those transitions are outside the current routing contract.

When that design is adopted, routing changes must be explicit and artifact-grounded. They must define exact committed state predicates, transition ownership, event/command triggers, and interaction with existing Evidence Request investigation.

Until then:

```text
absence of Target Role / Information Request / Information Response
≠ architecture defect
```

It is a deliberate MVP deferral.

---

# 31. Routing Trigger Points

Routing should run after meaningful committed Runtime Job state changes.

## Professional-State Trigger

For professional artifact changes, the sole canonical routing trigger is:

```text
artifact_committed
```

This Event represents the successfully committed professional-state mutation and is persisted in the same SQLite transaction as the professional commit.

Do not independently trigger routing from:

```text
execution_committed
```

`execution_committed` is audit/telemetry only.

This prevents one successful professional operation from creating duplicate `evaluate_routing` Commands.

## Non-Artifact Runtime Triggers

Lifecycle evaluation may also be requested after explicit non-artifact runtime events such as:

```text
job_created
interaction_completed
manual recovery action
```

when those events can legitimately change the next lifecycle decision.

Routing should not continuously poll professional state unless needed by implementation.


---

# 32. Routing After Professional Commit

Canonical sequence:

```text
Professional operation commits
        ↓
Runtime Job pointers advance
+
Execution marked committed
+
artifact_committed Event persisted
        ↓
artifact_committed
        ↓
Command: evaluate_routing
        ↓
Router loads current professional state
        ↓
Predicates evaluate
        ↓
BEGIN ROUTING TRANSACTION
  append routing decision
  update lifecycle.phase
  update lifecycle.entered_at
  increment Runtime Job revision
  persist lifecycle_changed Event
COMMIT
        ↓
Trello projection updates
```

If the routing transaction fails, none of the routing-history, lifecycle, revision, or `lifecycle_changed` changes become authoritative.

Routing failure after professional commit must not roll back professional state.

---

# 33. Routing and Trello

Trello is a projection of lifecycle state.

Example:

```text
Runtime Job:
lifecycle.phase = evaluation
```

may map to:

```text
Trello list:
Evaluation
```

The router does not inspect Trello list placement to decide professional routing.

If Trello is wrong:

```text
Runtime Job remains authoritative.
```

Synchronization should repair the board.

---

# 34. Routing Comments

Each meaningful transition may produce a Trello comment.

Example:

```text
Routing decision · ROUTE-0021

Evaluation → Analysis

Basis: EVAL-0004 v2

Reason: One blocking Evidence Uncertainty remains.
```

The authoritative decision remains in:

```text
Runtime Job.routing_history
```

---

# 35. Manual Review Routing

The Runtime Job may enter:

```text
manual_review
```

when deterministic routing is unsafe.

Examples:

- Inconsistent professional artifact state.
- Missing required current artifact.
- Invalid pointer combination.
- Repeated handler failure.
- Unresolvable commit conflict.
- Unsupported schema version.
- Runtime corruption.

Manual Review is not a professional conclusion.

It is a runtime safety state.

---

# 36. Health Overrides

Routing occurs only when health permits.

Recommended behavior:

```text
health == healthy
→ normal routing

health == degraded
→ normal routing allowed

health == recoverable_failure
→ normal routing paused

health == blocked
→ route/suspend to manual_review
```

A degraded Trello synchronization state must not stop professional lifecycle progression.

---

# 37. Cancelled Jobs

If:

```text
lifecycle.phase == cancelled
```

the router does nothing.

No professional operation may be scheduled automatically.

No lifecycle transition occurs.

---

# 38. Complete Jobs

If:

```text
lifecycle.phase == complete
```

the router does nothing.

V3 V0.1 does not support automatic reopening.

---

# 39. New Job Initialization

A new Runtime Job begins:

```text
new
```

Required starting state should include at minimum:

```text
Target Job pointer
Current JER set
```

When minimum inputs are available and Runtime Job health is valid:

```text
new
→ analysis
```

If required starting state is missing:

```text
manual_review
```

or remain:

```text
new
```

depending on whether missing state is expected or erroneous.

This distinction should be defined by Job creation handlers.

---

# 40. Routing Predicate Purity

Routing predicates should be pure functions where practical.

Example:

```python
def has_blocking_product_defects(evaluation) -> bool:
    ...
```

Properties:

- Same input state gives same result.
- No API calls.
- No mutation.
- No professional interpretation.
- No Trello/Discord side effects.

This makes routing highly testable.

---

# 41. Routing Function Shape

Conceptually:

```python
def derive_next_phase(job, professional_state):
    ...
```

Recommended behavior:

```text
input:
current committed Runtime Job state

output:
routing_decision
```

Side effects such as:

```text
append history
update lifecycle
post Trello comment
```

should occur outside the pure decision function where practical.

---

# 42. Routing Priority Model

Within each phase, predicates are evaluated in explicit order.

Example for `evaluation`:

```text
1. has_blocking_evidence_uncertainties
2. has_blocking_product_defects
3. is_ready_to_submit
4. otherwise invalid/incomplete evaluation state
```

Avoid relying on dictionary ordering or emergent control flow.

Priority should be defined in the routing table and tested.

---

# 43. Invalid Phase / Professional State Combinations

Examples:

```text
phase == evaluation
evaluation pointer == null
```

```text
phase == resume_production
JEA pointer == null
```

```text
phase == investigation
active_erqs == []
```

Such combinations should not trigger professional inference.

Recommended behavior:

```text
health → blocked
lifecycle → manual_review
```

unless the state is a recognized transient inside an atomic handler transition.

Handlers should minimize externally visible transient inconsistencies.

---

# 44. Routing History Noise Control

Routing history records meaningful lifecycle decisions, not predicate polling.

Append routing history when:

- Lifecycle phase changes.
- Manual Review is entered.
- A human recovery decision changes lifecycle.
- An explicitly identified meaningful runtime milestone justifies a deliberate self-transition.

Do not append routing history when:

- A periodic check finds the same state.
- Duplicate routing Commands evaluate the same current phase and basis.
- A self-transition reflects only incomplete work still remaining.
- No authoritative lifecycle decision changed.

Example not worth logging:

```text
investigation still waiting
```

every 30 seconds.

Example worth logging:

```text
All ERQs now have Evidence Responses.
Investigation → Evidence Integration.
```

Default rule:

```text
same phase + no explicit meaningful milestone
→ no routing_history append
```

---

# 45. Routing Reason Text

`reason` is human-readable runtime explanation.

It should be derived from predicate result and exact artifact basis.

Examples:

```text
"JEA-0004 v5 contains two open Material Evidence Needs."
```

```text
"EVAL-0003 v4 contains one blocking Evidence Uncertainty."
```

```text
"EVAL-0003 v5 is ready_to_submit with no blocking findings."
```

Do not generate speculative reasoning in routing comments.

---

# 46. Exact Artifact Basis

Every routing transition should identify the professional artifact state that justified it.

Examples:

```text
analysis route
→ JEA reference

evaluation route
→ Resume Evaluation reference

investigation completion
→ ERQ + Evidence Response references

evidence integration completion
→ relevant current JER + Evidence Response state
```

This allows deterministic audit and troubleshooting.

---

# 47. Router Does Not Modify Professional Pointers

The router may modify:

```text
lifecycle
routing_history
```

and runtime metadata necessary for the transition.

It must not modify:

```text
JER pointers
JEA pointer
ERQ pointers
Evidence Response pointers
Resume pointer
WCM pointer
Evaluation pointer
```

Those belong to handlers/commit logic.

---

# 48. ERQ Fan-Out and Router Responsibility

The router determines:

```text
evidence_request phase required
```

It does not decide Evidence Request content.

The evidence-request handler determines which unresolved Material Evidence Need lacks an ERQ and invokes:

```text
request_evidence
```

one coherent need at a time.

This keeps routing deterministic and professional request construction inside Researcher authority.

---

# 49. Investigation Completion

Investigation should not transition merely because:

```text
interaction.status == completed
```

Professional Evidence Response output must also commit successfully.

Required condition:

```text
has_erqs_awaiting_evidence_response == false
AND
has_unintegrated_evidence_responses == true
```

This means:
- Every current active ERQ has a committed current Evidence Response for that exact ERQ version.
- At least one committed Evidence Response remains to be integrated.

Then:

```text
investigation
→ evidence_integration
```

If `has_erqs_awaiting_evidence_response == true`, the Job remains in `investigation` even when one or more Evidence Responses have already committed.

Discord interaction completion alone is insufficient.

---

# 50. Evidence Integration Completion

Evidence integration is complete only when:

```text
unintegrated_evidence_responses == []
```

after successful authoritative evidence commits.

Then:

```text
evidence_integration
→ analysis
```

---

# 51. Product Defect Loop

```text
Evaluation
    ↓
blocking Product Defect
    ↓
Resume Production
    ↓
new Resume + WCM
    ↓
Evaluation
```

The Writer may receive the current Resume Evaluation as product feedback.

The router only controls lifecycle.

---

# 52. Evidence Uncertainty Loop

```text
Evaluation
    ↓
blocking Evidence Uncertainty
    ↓
Analysis
    ↓
Researcher reconciliation
    ↓
├── existing evidence resolves
│      ↓
│   Resume Production
│
├── Material Evidence Need
│      ↓
│   Evidence Request
│      ↓
│   Investigation
│
└── known limitation
       ↓
    Resume Production
```

The router does not predetermine which Researcher outcome occurs.

---

# 53. Candidate Limitation Path

```text
Evaluation
    ↓
Candidate Limitation(s)
+
no blocking findings
+
ready_to_submit
    ↓
Complete
```

No special routing predicate is required.

---

# 54. V0.1 Acceptance Criteria

The Routing Model is acceptable when:

- [ ] Router uses committed current professional state only.
- [ ] Router predicates are deterministic.
- [ ] Schema fields are preferred over narrative interpretation.
- [ ] Analysis routes based on Material Evidence Need state.
- [ ] Evidence Request phase remains until current unresolved needs have ERQs.
- [ ] `has_active_erqs` and `has_erqs_awaiting_evidence_response` have distinct deterministic meanings.
- [ ] Investigation exits only when no current active ERQ awaits a committed Evidence Response and unintegrated Evidence Responses exist.
- [ ] ERQ receipt of Evidence Response does not automatically equal resolution.
- [ ] Evidence integration always returns through analysis.
- [ ] Blocking Evidence Uncertainty outranks blocking Product Defect.
- [ ] Blocking Product Defects return to resume production.
- [ ] Candidate Limitations do not directly route.
- [ ] Ready-to-submit state terminates the Job when no blocking findings remain.
- [ ] Invalid professional/runtime combinations fail safely.
- [ ] Routing decisions are append-only and artifact-grounded.
- [ ] `artifact_committed` is the sole canonical professional-state routing trigger.
- [ ] `execution_committed` never independently causes professional routing.
- [ ] Routing-history append, lifecycle transition, entered-at update, Runtime Job revision increment, and `lifecycle_changed` Event persist atomically.
- [ ] Trello may mirror routing but is not authoritative.
- [ ] Router never changes professional artifact pointers.
- [ ] Manual Review exists for unsafe deterministic state.
- [ ] Complete and cancelled states do not automatically reopen.
- [ ] Routine no-change evaluations do not append routing history.
- [ ] Self-transitions are recorded only for explicit meaningful milestones.
- [ ] Duplicate or periodic routing checks over unchanged state remain no-ops.
- [ ] V0.1 routing explicitly excludes deferred Target Role, Information Request, and Information Response predicates.
- [ ] Future Analyst/Custodian routing concepts require an explicit architecture update rather than implicit runtime inference.

---

# Next Design Step

After this model is accepted, define the:

> **V3 Event Model**

The Event Model should specify:

- Internal runtime event envelope.
- Event identity and deduplication.
- Event sources.
- Trello webhook normalization.
- Discord event normalization.
- Artifact commit events.
- Routing events.
- Handler scheduling events.
- Delivery guarantees.
- Event ordering.
- Event retry.
- Dead-letter/manual-review behavior.