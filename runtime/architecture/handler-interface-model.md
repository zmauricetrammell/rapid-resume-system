# V3: Split Researcher into Analyst and Custodian

## Objective

Refactor the current Researcher role into two independent professional roles:

- **Analyst** — owns target interpretation, evidence requirements, evidence sufficiency, transferability, fit analysis, and Job Experience Analysis.
- **Custodian** — owns authoritative professional evidence storage, retrieval, reconciliation, and integration.

The goal is to reduce concentration of epistemic authority, prevent premature target-driven over-optimization of professional evidence, and establish a cleaner interface between target analysis and professional evidence custody.

This change was identified during V3 runtime design while defining the Evidence Integration handler.

---

# Problem

The current Researcher combines several distinct responsibilities:

```text
Target Job analysis
      ↓
Evidence requirement definition
      ↓
Professional evidence search
      ↓
Evidence selection
      ↓
Evidence sufficiency judgment
      ↓
Missing-information identification
      ↓
Evidence Request generation
      ↓
New evidence integration
      ↓
Re-analysis
```

This gives one professional role authority over both:

1. **What evidence would satisfy the target**, and
2. **What evidence exists and how authoritative professional records are changed.**

That creates unnecessary coupling and a risk of early target-driven evidence optimization.

The current Researcher can effectively:

```text
decide what would prove X
→ search for X-like evidence
→ interpret evidence against X
→ request missing evidence
→ modify the evidence repository
→ reassess X
```

Even with strong contracts, this places too much analytical and evidentiary authority in one role.

---

# Proposed Architecture

Split Researcher into:

```text
ANALYST
+
CUSTODIAN
```

Conceptually:

```text
Target Job / Target Role Research
              │
              ▼
           ANALYST
              │
              ▼
      Information Request
              │
              ▼
          CUSTODIAN
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
Evidence exists   Material fact missing
       │             │
       │             ▼
       │      Evidence Request
       │             │
       │             ▼
       │        INTERVIEWER
       │             │
       │             ▼
       │      Evidence Response
       │             │
       │             ▼
       │         CUSTODIAN
       │      integrate evidence
       │             │
       └──────┬──────┘
              ▼
      Information Response
              │
              ▼
           ANALYST
              │
              ▼
             JEA
              │
              ▼
           WRITER
              │
              ▼
       Resume + WCM
              │
              ▼
         EVALUATOR
```

---

# Core Separation

## Analyst

The Analyst answers:

> What professional evidence would convincingly support this target?

The Analyst owns:

- Target-role interpretation.
- Job-description analysis.
- Future deep target/company research.
- Requirement decomposition.
- Evidence specification.
- Evidence sufficiency.
- Evidence relevance.
- Evidence transferability.
- Requirement coverage.
- Candidate fit.
- Functional Role Architecture.
- Claim constraints derived from target/evidence comparison.
- Job Experience Analysis.

The Analyst does **not** own authoritative professional evidence storage.

The Analyst should not directly modify JERs.

---

## Custodian

The Custodian answers:

> What authoritative professional evidence do we actually have?

The Custodian owns:

- Job Experience Record custody.
- Professional evidence retrieval.
- Evidence provenance.
- Evidence conflict preservation.
- Evidence-response reconciliation.
- Authoritative evidence integration.
- Professional evidence versioning.
- Evidence Request generation when an Analyst-authorized information request cannot be resolved from current authoritative state.

The Custodian does **not** determine target-job fit.

The Custodian should not independently decide that a capability matters merely because a job description requests it.

---

# Architectural Principle

> **Analyst specifies the professional information needed. Custodian determines what authoritative information exists.**

This creates an adversarial professional boundary before resume writing.

The Analyst is incentivized to ask:

> What would prove this requirement?

The Custodian is constrained to answer:

> This is what the professional record actually supports.

---

# New Analyst ↔ Custodian Interface

Introduce a professional request/response interface between Analyst and Custodian.

Working names:

```text
Information Request
Information Response
```

Alternative naming may be considered during schema design.

---

# Information Request

The Analyst produces an Information Request describing the professional facts needed to evaluate a target requirement or analytical question.

Conceptual example:

```yaml
information_request:

  requirement_id: REQ-007

  evidence_sought:
    capability: direct service desk people management

    dimensions:
      - direct-report relationship
      - team size
      - duration
      - performance management
      - coaching
      - measurable workforce outcomes

  materiality: high

  target_context:
    requirement: >
      Directly manage 8-10 service desk analysts.

  constraints:
    - do not infer direct reporting from general department leadership
```

The request defines the analytical need.

It does not prescribe what the professional evidence must say.

---

# Information Response

The Custodian returns an Information Response grounded only in authoritative professional state.

Conceptually:

```yaml
information_response:

  request_id: INFOREQ-001

  status: partially_resolved

  evidence:
    - JER-0004:v3
    - JER-0011:v2

  resolved_dimensions:
    - team size
    - duration
    - coaching

  unresolved_dimensions:
    - direct-report relationship

  negative_evidence: []

  known_limitations: []

  provenance:
    ...
```

The Analyst then determines what that evidence means for target fit.

---

# Missing Information Resolution

When current authoritative professional evidence cannot satisfy an Information Request, the Custodian may determine that a factual dimension remains unresolved.

The Custodian may generate an Evidence Request only when:

1. The Analyst's Information Request establishes that the factual dimension is materially needed.
2. Current authoritative evidence cannot resolve it.
3. Human factual investigation could reasonably resolve or materially improve it.

This preserves separation:

```text
Analyst
→ determines materiality

Custodian
→ determines evidence availability

Interviewer
→ establishes missing facts
```

---

# Recursive Resolution Model

Preferred flow:

```text
Analyst
      │
      ▼
Information Request
      │
      ▼
Custodian search
      │
      ├── sufficient evidence
      │        │
      │        ▼
      │  Information Response
      │
      └── unresolved material fact
               │
               ▼
         Evidence Request
               │
               ▼
          Interviewer
               │
               ▼
         Evidence Response
               │
               ▼
          Custodian
      integrate authoritative evidence
               │
               ▼
      rerun Information Request
               │
               ▼
      Information Response
               │
               ▼
            Analyst
```

The Analyst receives the resolved professional evidence state rather than managing the evidence-acquisition loop itself.

---

# Recursion Boundary

Custodian evidence acquisition must remain bounded by the originating Information Request.

The Custodian must not recursively search for increasingly impressive or target-optimized facts beyond the requested professional dimensions.

Example:

```text
Analyst asks:
"What was the candidate's direct-report relationship to the 10-person service desk?"

Custodian may investigate:
- direct
- indirect
- mixed
- unresolved

Custodian may not expand the investigation into:
"Find any additional leadership accomplishments that would strengthen the resume."
```

---

# Read / Write Separation

Custodian operations should have single-purpose professional semantics.

## Read Operation

```text
retrieve_evidence
```

Purpose:

- Search authoritative professional records.
- Return evidence relevant to an Information Request.
- Do not mutate authoritative evidence.

## Write Operation

```text
integrate_evidence
```

Purpose:

- Reconcile confirmed Evidence Responses into authoritative professional records.
- Create/update JER state.
- Do not simultaneously perform target-fit analysis.

The same Custodian role may perform both operations, but one invocation should have one professional purpose.

---

# Custodian Invocation Invariant

> **A Custodian invocation either retrieves authoritative professional evidence or integrates authoritative professional evidence. It does not perform both professional operations in the same invocation.**

An integration operation may necessarily read existing records to perform safe mutation, but its professional purpose remains write/reconciliation rather than target-specific evidence retrieval.

---

# Analyst Responsibilities

Proposed Analyst operations:

```text
analyze_target
request_information
generate_analysis
```

Exact task boundaries should be designed.

The Analyst should eventually be able to analyze more than the literal job description.

Future inputs may include:

- Company research.
- Similar job postings.
- Hiring-manager public statements.
- Organizational structure.
- Company engineering/IT publications.
- Market expectations.
- Role-family patterns.

This may eventually produce a richer:

```text
Target Role Model
```

The Custodian interface should remain unchanged regardless of how target requirements are derived.

---

# Custodian Responsibilities

Proposed Custodian operations:

```text
retrieve_evidence
request_evidence
integrate_evidence
```

Exact task boundaries should be designed.

Custodian remains authoritative for JER state.

---

# Interviewer Boundary

Interviewer remains responsible only for human factual investigation.

Flow:

```text
Evidence Request
      ↓
Interviewer
      ↓
Human investigation
      ↓
Evidence Response
```

Interviewer does not determine:

- Target relevance.
- Evidence strength.
- Evidence sufficiency.
- Transferability.
- Job fit.
- JER integration.

---

# Writer Boundary

Writer remains unchanged conceptually.

Writer consumes Analyst-authorized analytical state.

```text
JEA
→ Writer
→ Resume + WCM
```

Writer does not independently query the Custodian.

---

# Evaluator Boundary

Evaluator remains the downstream adversarial product-review layer.

The Analyst/Custodian split creates an earlier adversarial boundary:

```text
Analyst
vs
Custodian
```

while Evaluator remains:

```text
Target objective
vs
finished resume product
```

These controls address different failure modes.

---

# Expected Benefits

## Reduced Early Over-Optimization

The same professional role no longer:

```text
defines desired evidence
+
searches evidence
+
interprets evidence
+
modifies evidence
```

---

## Stronger Evidence Integrity

Custodian optimizes for:

```text
accuracy
provenance
completeness
conflict preservation
```

rather than target fit.

---

## Stronger Analytical Independence

Analyst can challenge evidence sufficiency without owning evidence custody.

---

## Cleaner V3 Runtime Interfaces

Runtime operations become easier to define:

```text
analyze target
retrieve evidence
request evidence
investigate
integrate evidence
analyze evidence
write resume
evaluate resume
```

---

## Future Deep Target Research

The Analyst can evolve beyond literal job-description interpretation without requiring changes to professional evidence custody.

---

## Better Testing

Analyst and Custodian behavior can be tested independently.

Examples:

```text
Given an Information Request,
does Custodian return all and only supported evidence?
```

```text
Given an Information Response,
does Analyst classify requirement coverage conservatively?
```

---

# V3 Runtime Impact

This split changes the expected handler model.

Instead of:

```text
GenerateAnalysisHandler
RequestEvidenceHandler
EvidenceIntegrationHandler
```

all centered on Researcher, V3 may eventually use:

```text
AnalyzeTargetHandler

RetrieveEvidenceHandler

RequestEvidenceHandler

InvestigationHandler

IntegrateEvidenceHandler

GenerateAnalysisHandler

GenerateResumeHandler

EvaluateResumeHandler
```

Exact handler decomposition should follow finalized professional task boundaries.

---

# Routing Impact

The current Routing Model assumes:

```text
analysis
→ evidence_request
```

based directly on JEA Material Evidence Needs.

The split may introduce a professional evidence-resolution cycle before final JEA generation.

Conceptually:

```text
target_analysis
      ↓
information_request
      ↓
evidence_retrieval
      ↓
├── evidence complete
│      ↓
│   analysis
│
└── evidence incomplete
       ↓
   evidence_request
       ↓
   investigation
       ↓
   evidence_integration
       ↓
   evidence_retrieval
```

The Runtime Job and Routing Model must be reviewed after professional interfaces are finalized.

---

# Artifact Impact

Potential new artifacts:

```text
Information Request
Information Response
```

Potential future artifact:

```text
Target Role Model
```

Existing artifacts likely retained:

```text
JER
Evidence Request
Evidence Response
JEA
Resume
WCM
Resume Evaluation
Process Feedback
```

Exact schemas should be designed only after role/task boundaries are approved.

---

# Migration Considerations

The current Researcher role should not be deleted until equivalent Analyst and Custodian responsibilities are fully defined.

Migration should:

1. Inventory current Researcher authorities.
2. Assign each authority to Analyst or Custodian.
3. Identify any authority that should disappear.
4. Define new task boundaries.
5. Define Analyst/Custodian artifacts.
6. Update schemas.
7. Update V3 routing assumptions.
8. Update handler interface design.
9. Validate against previously successful V2 jobs.
10. Remove legacy Researcher role only after parity is demonstrated.

---

# Compatibility Goal

The split should preserve the successful behavior already validated during V2 testing.

Existing successful final products should remain reproducible or improve.

The refactor should not reduce:

- Evidence completeness.
- Resume quality.
- Traceability.
- Human investigation quality.
- Candidate-fit accuracy.

---

# Non-Goals

This issue does not yet:

- Implement Analyst or Custodian.
- Finalize new schemas.
- Finalize handler code.
- Redesign Writer.
- Redesign Evaluator.
- Change Interviewer authority.
- Decide the future Target Role Model.
- Introduce arbitrary recursive evidence exploration.
- Make Custodian responsible for target-job interpretation.
- Make Analyst responsible for JER mutation.

---

# Design Questions

The implementation/design work should resolve:

- [ ] Exact Analyst contract.
- [ ] Exact Custodian contract.
- [ ] Analyst task boundaries.
- [ ] Custodian task boundaries.
- [ ] Information Request schema.
- [ ] Information Response schema.
- [ ] Whether `request_evidence` belongs exclusively to Custodian.
- [ ] Exact trigger for recursive human evidence resolution.
- [ ] Exact completion condition for an Information Request.
- [ ] JER integration semantics.
- [ ] Whether JEA remains Analyst output.
- [ ] Whether a Target Role Model is needed now or later.
- [ ] How product-feedback Evidence Uncertainty reaches Analyst/Custodian.
- [ ] V3 Runtime Job changes.
- [ ] V3 Routing Model changes.
- [ ] V3 Handler Interface changes.

---

# Acceptance Criteria

The Analyst/Custodian split is ready for implementation when:

- [ ] No professional authority is ambiguously shared.
- [ ] Analyst cannot mutate authoritative professional evidence.
- [ ] Custodian cannot determine target-job fit.
- [ ] Custodian retrieval is target-query bounded.
- [ ] Custodian read and write operations have separate task semantics.
- [ ] Analyst expresses evidence needs through a structured professional artifact.
- [ ] Custodian responds through a structured professional artifact.
- [ ] Missing material facts can enter the Interviewer loop without workflow awareness inside professional agents.
- [ ] Confirmed Evidence Responses return to Custodian for integration.
- [ ] Analyst receives authoritative evidence results after evidence resolution.
- [ ] JEA generation remains traceable to exact professional evidence state.
- [ ] Existing successful V2 resume workflows remain reproducible.
- [ ] V3 handlers and routing can invoke the new professional operations deterministically.

---

# Definition of Done

The current Researcher concentration of authority is replaced by two independent professional roles:

```text
Analyst
→ defines and evaluates professional information needs against the target

Custodian
→ retrieves, preserves, and integrates authoritative professional evidence
```

The resulting architecture must preserve:

- Professional evidence integrity.
- Target-analysis independence.
- Human evidence investigation.
- Partner independence.
- Deterministic V3 orchestration.
- Existing Writer/Evaluator interfaces where practical.

This issue is complete when the Analyst/Custodian professional interfaces are stable enough for the V3 Handler Interface and Routing Models to be finalized.