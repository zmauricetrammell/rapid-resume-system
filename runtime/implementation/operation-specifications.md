# RRS V3 Operation Specification Definitions

## Status

Implementation Planning — Phase 6

## Purpose

This document defines the six current V0.1 professional operations in concrete implementation-planning terms.

It translates the frozen Operation Specification Registry architecture into explicit specifications for:

```text
generate_analysis
request_evidence
investigate_evidence_request
integrate_evidence
generate_resume
evaluate_resume
```

For each operation, this document defines:

- allowed lifecycle phases,
- professional binding,
- required and optional inputs,
- identity dependencies,
- freshness dependencies,
- retrieval requirements,
- required outputs,
- coupled output groups,
- schema bindings,
- pointer/collection mutation authority,
- deterministic reconciliation hooks,
- retry policy reference,
- handler key.

This is still implementation planning, not production configuration syntax.

The final implementation may serialize these definitions as YAML, immutable Python objects, or another deterministic configuration form.

---

# 1. Global Rules

Every effective Operation Specification must satisfy these rules:

1. `operation_type` is unique.
2. `handler_key` resolves to one registered handler implementation.
3. allowed lifecycle phases are explicit.
4. required professional inputs are explicit.
5. optional inputs are explicit.
6. identity dependencies are explicit.
7. freshness dependencies are explicit.
8. retrieval requirement is explicit.
9. output contract is explicit.
10. coupled products are explicit.
11. schema references are exact.
12. pointer/collection authority is explicit.
13. deterministic reconciliation hooks are explicit.
14. retry policy reference is explicit.
15. professional role binding is configuration, not handler identity.
16. semantic specification identity is derived from effective semantics/resources, not incidental Git SHA.
17. handlers cannot widen specification authority.

---

# 2. Canonical Retry Policy References

Initial planning references:

```text
professional_default
professional_evidence_required
professional_interviewer
professional_integration
professional_resume
professional_evaluation
```

These names are configuration references only.

Exact retry counts/backoff belong to implementation configuration.

---

# 3. Canonical Handler Keys

Recommended:

```text
generate_analysis
request_evidence
investigate_evidence_request
integrate_evidence
generate_resume
evaluate_resume
```

Current V0.1 handlers may use one handler per operation even when several share a common framework.

---

# 4. `generate_analysis`

## Purpose

Produce the current Job Experience Analysis from the Target Job and authoritative reusable professional evidence.

## Allowed Lifecycle Phases

```text
analysis
```

## Professional Binding

```text
professional_role: researcher
contract: agents/researcher/contract.md
task: agents/researcher/tasks/generate-analysis.md
```

## Required Inputs

```text
target_job
jer_set
```

## Optional Inputs

```text
resume_evaluation
unintegrated_evidence_responses
```

The Researcher may use current product feedback and new Evidence Responses when analysis is being regenerated.

## Identity Dependencies

```text
target_job
jer_set
resume_evaluation when present and authorized for analysis
unintegrated_evidence_responses when present and relevant
researcher contract
generate_analysis task
JEA schema
retrieval result fingerprint when retrieval is used
```

## Freshness Dependencies

```text
target_job
jer_set
resume_evaluation when included
unintegrated_evidence_responses when included
```

## Retrieval

```text
requirement: required
evidence_source: configured reusable-professional-evidence source
```

The Researcher operation may require broad evidence retrieval from the professional evidence corpus.

Successful zero-match retrieval is distinct from retrieval failure.

## Required Outputs

```text
job_experience_analysis
```

## Coupled Groups

```text
none
```

## Output Schema

```text
schemas/job-experience-analysis.yaml
```

## Pointer Authority

```text
JEA
→ SET
```

## Deterministic Reconciliation

Potential hook:

```text
reconcile_active_erqs_from_jea
```

The hook may compare schema-defined current Material Evidence Needs against active ERQ state, but must not perform professional reasoning.

## Retry Policy

```text
professional_evidence_required
```

## Handler Key

```text
generate_analysis
```

---

# 5. `request_evidence`

## Purpose

Produce one or more Evidence Requests for unresolved Material Evidence Needs identified in the current JEA.

## Allowed Lifecycle Phases

```text
evidence_request
```

## Professional Binding

```text
professional_role: researcher
contract: agents/researcher/contract.md
task: agents/researcher/tasks/request-evidence.md
```

## Required Inputs

```text
job_experience_analysis
target_job
```

## Optional Inputs

```text
active_erqs
```

Existing active ERQs may be supplied so the Researcher does not duplicate already-covered evidence questions.

## Identity Dependencies

```text
current JEA
target_job
active_erqs when supplied
researcher contract
request_evidence task
Evidence Request schema
```

## Freshness Dependencies

```text
current JEA
active_erqs
```

The output must not commit if the underlying Material Evidence Need state changed.

## Retrieval

```text
requirement: none
```

This operation should operate from current professional analysis state rather than broad evidence retrieval unless later architecture explicitly changes that rule.

## Required Outputs

```text
evidence_request
```

The operation may produce multiple ERQs when the task/schema supports multiple outputs.

## Coupled Groups

If multiple ERQs are required to satisfy the operation's output contract:

```text
all required ERQs from one operation commit as one logical output group
```

Exact grouping depends on final extractor shape.

## Output Schema

```text
schemas/evidence-request.yaml
```

## Pointer Authority

```text
active_erqs
→ ADD

active_erqs
→ UPSERT_VERSION
```

No authority to mutate JERs, JEA, Resume, WCM, or Evaluation.

## Deterministic Reconciliation

Potential hook:

```text
reconcile_active_erqs_from_jea
```

Used after commit if needed to remove/replace ERQs whose schema-defined source need is no longer current.

## Retry Policy

```text
professional_default
```

## Handler Key

```text
request_evidence
```

---

# 6. `investigate_evidence_request`

## Purpose

Conduct collaborative human investigation of one current Evidence Request and produce either the next conversation turn or a completed Evidence Response.

## Allowed Lifecycle Phases

```text
investigation
```

## Professional Binding

```text
professional_role: interviewer
contract: agents/interviewer/contract.md
task: agents/interviewer/tasks/investigate-evidence-request.md
```

## Required Inputs

```text
current evidence_request
persisted ordered Interaction conversation
exact current unprocessed authorized human-message batch
```

## Optional Inputs

```text
target_job
relevant professional context explicitly authorized by task/specification
```

Do not silently widen Interviewer context beyond the Operation Specification.

## Identity Dependencies

For one continuation:

```text
interaction_id
current ERQ artifact ID + version
last persisted Interviewer turn boundary
exact ordered human-message IDs in current batch
Interviewer contract
investigate_evidence_request task
Evidence Response schema
```

## Freshness Dependencies

```text
current ERQ artifact ID + version
Interaction status
exact human-message batch still unprocessed
```

## Retrieval

```text
requirement: none
```

The Interviewer investigates the human, not the reusable evidence corpus.

## Result Type

```text
InterviewerContinuationResult
=
ConversationTurn
|
CompletedProfessionalArtifact
```

## ConversationTurn Path

No professional artifact output commits.

Transaction consumes exact human messages and persists the next Interviewer conversational message.

## CompletedProfessionalArtifact Path

V0.1 restriction:

```text
artifact_type == evidence_response
```

## Required Professional Output

```text
evidence_response
```

when the continuation completes.

## Output Schema

```text
schemas/evidence-response.yaml
```

## Pointer Authority

```text
unintegrated_evidence_responses
→ ADD
```

The completed Evidence Response professional commit also consumes the exact human-message batch.

## Coupled Transaction Requirement

```text
Evidence Response artifact metadata
+
unintegrated_evidence_responses ADD
+
exact consumed human messages → processed
+
Execution finalization
+
artifact_committed
```

commit atomically.

## Deterministic Reconciliation

```text
none
```

Interaction completion is a later deterministic `complete_interaction` command.

## Retry Policy

```text
professional_interviewer
```

## Handler Key

```text
investigate_evidence_request
```

---

# 7. `integrate_evidence`

## Purpose

Reconcile completed Evidence Responses into authoritative reusable Job Experience Records and current Job evidence state.

## Allowed Lifecycle Phases

```text
evidence_integration
```

## Professional Binding

```text
professional_role: researcher
contract: agents/researcher/contract.md
task: evidence-integration behavior defined by current Researcher contract/task set
```

Important implementation note:

If the repository does not currently contain a dedicated `integrate-evidence.md` task, implementation planning must not invent professional instructions silently.

The effective specification must bind to the actual approved professional task resource before implementation.

## Required Inputs

```text
current jer_set
unintegrated_evidence_responses
current JEA when required for context/reconciliation
```

## Optional Inputs

```text
target_job
active_erqs
```

## Identity Dependencies

```text
exact JER versions being integrated
exact Evidence Response versions
current JEA when supplied
Researcher contract
integration task resource
JER schema
```

## Freshness Dependencies

```text
JER versions being changed
Evidence Responses being consumed
current JEA when relevant
```

## Retrieval

Recommended:

```text
requirement: optional
```

If the Researcher needs additional reusable evidence to reconcile a response safely, retrieval may be authorized by the final task/specification.

If the approved task does not require it:

```text
requirement: none
```

This must be confirmed against the final professional task resource before code.

## Required Outputs

```text
one or more new job_experience_record versions
```

## Coupled Group

```text
all required new JER versions
+
all Evidence Responses consumed by this integration
```

form one logical commit group.

## Output Schema

```text
schemas/job-experience-record.yaml
```

## Pointer Authority

```text
jer_set
→ UPSERT_VERSION

unintegrated_evidence_responses
→ REMOVE
```

Potentially:

```text
active_erqs
→ REMOVE
```

only if deterministic schema-defined reconciliation authorizes removal after integration/re-analysis. Prefer leaving ERQ resolution to subsequent analysis unless architecture/task explicitly requires direct removal here.

## Deterministic Reconciliation

Potential:

```text
none before re-analysis
```

Canonical architecture prefers Researcher re-analysis to determine whether evidence needs are actually resolved.

## Retry Policy

```text
professional_integration
```

## Handler Key

```text
integrate_evidence
```

---

# 8. `generate_resume`

## Purpose

Produce the targeted Resume and Writer Content Manifest from the current authoritative analysis and professional evidence.

## Allowed Lifecycle Phases

```text
resume_production
```

## Professional Binding

```text
professional_role: writer
contract: agents/writer/contract.md
task: agents/writer/tasks/generate-resume.md
```

## Required Inputs

```text
target_job
current JEA
current jer_set
resume skeleton
prompt bank
```

## Optional Inputs

```text
current resume_evaluation
current resume
other explicitly authorized presentation resources
```

A current Evaluation may be supplied when regenerating the product after product defects.

## Identity Dependencies

```text
target_job
current JEA
current jer_set
resume skeleton
prompt bank
current resume_evaluation when supplied
Writer contract
generate_resume task
Writer Content Manifest schema
output-format/template identities
```

## Freshness Dependencies

```text
target_job
current JEA
current jer_set
current resume_evaluation when supplied
```

Presentation resources that materially affect output participate in logical identity.

## Retrieval

```text
requirement: none
```

The Writer does not independently search the broad professional evidence corpus.

It uses the authorized evidence/analysis supplied by the runtime.

## Required Outputs

```text
targeted_resume
writer_content_manifest
```

## Coupled Group

```text
[targeted_resume, writer_content_manifest]
```

Both must validate/finalize before either becomes current.

## Output Schemas

```text
Writer Content Manifest
→ schemas/writer-content-manifest.yaml

Targeted Resume
→ format/template contract rather than YAML schema
```

Resume format validation may include:

```text
file exists
expected document type
required structural sections
template/skeleton conformance checks
```

## Pointer Authority

```text
resume
→ SET

wcm
→ SET
```

No authority over JEA/JER/ERQ/Evidence Response/Evaluation.

## Deterministic Reconciliation

```text
none
```

## Retry Policy

```text
professional_resume
```

## Handler Key

```text
generate_resume
```

---

# 9. `evaluate_resume`

## Purpose

Independently evaluate the current Resume/WCM against the target role and authorized professional state.

## Allowed Lifecycle Phases

```text
evaluation
```

## Professional Binding

```text
professional_role: evaluator
contract: agents/evaluator/contract.md
task: agents/evaluator/tasks/evaluate-resume.md
```

## Required Inputs

```text
target_job
current resume
current WCM
current JEA
```

## Optional Inputs

```text
current jer_set
other supporting evidence required for factual-integrity verification
```

## Identity Dependencies

```text
target_job
resume
WCM
JEA
supporting evidence when included
Evaluator contract
evaluate_resume task
Resume Evaluation schema
```

## Freshness Dependencies

```text
target_job
resume
WCM
JEA
```

If supporting evidence is part of the evaluation's factual-integrity basis, include the exact supplied versions.

## Retrieval

Recommended:

```text
requirement: none
```

The Evaluator should judge the current product from supplied authoritative state rather than independently broaden the evidence corpus.

If factual-integrity verification later requires retrieval, that must be an explicit specification change.

## Required Outputs

```text
resume_evaluation
```

## Coupled Groups

```text
none
```

## Output Schema

```text
schemas/resume-evaluation.yaml
```

## Pointer Authority

```text
evaluation
→ SET
```

No direct authority over Resume/WCM/JEA/JER state.

## Deterministic Reconciliation

```text
none
```

Routing uses schema-defined Evaluation state such as:

```text
blocking product defects
blocking evidence uncertainties
is_ready_to_submit
```

## Retry Policy

```text
professional_evaluation
```

## Handler Key

```text
evaluate_resume
```

---

# 10. Operation Summary Matrix

| Operation | Lifecycle | Role | Retrieval | Required Output | Pointer Authority |
|---|---|---|---|---|---|
| `generate_analysis` | analysis | Researcher | required | JEA | `jea SET` |
| `request_evidence` | evidence_request | Researcher | none | ERQ | `active_erqs ADD/UPSERT_VERSION` |
| `investigate_evidence_request` | investigation | Interviewer | none | Evidence Response when complete | `unintegrated_evidence_responses ADD` |
| `integrate_evidence` | evidence_integration | Researcher | none/optional pending task confirmation | JER version(s) | `jer_set UPSERT_VERSION`, consumed responses `REMOVE` |
| `generate_resume` | resume_production | Writer | none | Resume + WCM | `resume SET`, `wcm SET` |
| `evaluate_resume` | evaluation | Evaluator | none | Resume Evaluation | `evaluation SET` |

---

# 11. Operation Identity Summary

## `generate_analysis`

Changes when materially relevant:

```text
Target Job
JER set
included Evaluation
included Evidence Responses
Researcher resources
JEA schema
retrieval result fingerprint
```

## `request_evidence`

Changes when:

```text
JEA
active ERQ state
Researcher resources
ERQ schema
```

## `investigate_evidence_request`

Changes per continuation when:

```text
ERQ version
prior conversation boundary
exact human message batch
Interviewer resources
Evidence Response schema
```

## `integrate_evidence`

Changes when:

```text
JER versions
Evidence Responses
integration professional resources
JER schema
```

## `generate_resume`

Changes when:

```text
Target Job
JEA
JER set
Evaluation if supplied
skeleton
prompt bank
Writer resources
WCM schema/template
```

## `evaluate_resume`

Changes when:

```text
Target Job
Resume
WCM
JEA
supporting evidence if supplied
Evaluator resources
Evaluation schema
```

---

# 12. Freshness Summary

Freshness determines commit eligibility, not merely operation identity.

A professional output may have been valid when invoked but become stale before commit.

Examples:

```text
JEA generated from JER v3
JER becomes v4 before commit
→ stale when jer_set is declared freshness dependency
```

```text
Resume generated from JEA v2
JEA becomes v3 before commit
→ stale
```

```text
Evaluation generated from Resume v4
Resume becomes v5 before commit
→ stale
```

Unrelated Runtime Job revision changes do not automatically make an Execution stale.

---

# 13. Retrieval Authority Summary

Recommended current V0.1 policy:

```text
generate_analysis
→ required evidence retrieval

request_evidence
→ none

investigate_evidence_request
→ none

integrate_evidence
→ pending confirmation from approved integration task
   default none unless explicitly authorized

generate_resume
→ none

evaluate_resume
→ none
```

This preserves professional evidence authority with the Researcher and prevents Writer/Evaluator from independently expanding the evidence corpus.

---

# 14. Mutation Authority Summary

## Researcher Analysis

```text
jea SET
```

## Researcher Evidence Request

```text
active_erqs ADD
active_erqs UPSERT_VERSION
```

## Interviewer Completion

```text
unintegrated_evidence_responses ADD
```

## Researcher Evidence Integration

```text
jer_set UPSERT_VERSION
unintegrated_evidence_responses REMOVE
```

## Writer

```text
resume SET
wcm SET
```

## Evaluator

```text
evaluation SET
```

No role identity grants these permissions independently.

They come only from the resolved Operation Specification.

---

# 15. Coupled Product Rules

V0.1 coupled professional commits:

## Resume Product

```text
Resume
+
Writer Content Manifest
```

must commit together.

## Evidence Integration

```text
all required new JER versions
+
consumed Evidence Response mutations
```

must commit together.

## Interviewer Evidence Response

```text
Evidence Response
+
exact consumed human-message batch
```

must commit together in the professional commit transaction.

---

# 16. Schema Binding Rules

Each professional structured artifact uses the exact approved schema:

```text
JER
→ schemas/job-experience-record.yaml

JEA
→ schemas/job-experience-analysis.yaml

ERQ
→ schemas/evidence-request.yaml

Evidence Response
→ schemas/evidence-response.yaml

WCM
→ schemas/writer-content-manifest.yaml

Resume Evaluation
→ schemas/resume-evaluation.yaml

Process Feedback
→ schemas/process-feedback.yaml
```

Targeted Resume uses document/template validation rather than a shared YAML professional artifact schema.

The exact schema supplied to the professional agent must equal the schema used for runtime validation.

---

# 17. Startup Registry Validation

Before runtime readiness, validate each specification:

```text
operation_type unique
handler_key exists
professional contract path exists
task path exists
required schema paths exist
allowed lifecycle phases valid
retrieval configuration resolves
pointer authority targets valid Runtime Job state
mutation types valid
required outputs declared
coupled groups reference declared outputs
identity/freshness dependencies reference authorized inputs/resources
retry policy exists
```

If any fail:

```text
runtime not ready
```

---

# 18. Specification Hash Inputs

Semantic Operation Specification hash should include canonical effective semantics:

```text
operation_type
handler_key
allowed lifecycle phases
professional binding content identities
input declarations
identity dependencies
freshness dependencies
retrieval declaration
output contract
schema/resource semantic hashes
pointer authority
deterministic reconciliation declarations
retry policy semantic identity when materially relevant
```

Do not include Git SHA merely because the specification was loaded from that revision.

Git/build identity is separate provenance.

---

# 19. Professional Resource Binding

Each specification binds exact professional resources through semantic content identity.

Conceptually:

```text
contract ResourceRef
task ResourceRef
schema ResourceRef(s)
templates/resources
```

If resource content changes materially:

```text
resource hash changes
→ semantic specification/resource identity changes
→ affected operation identity changes
```

---

# 20. Handler Contract

For all six operations:

```python
handler.execute(
    job_id,
    command,
    resolved_specification,
)
```

The handler may:

- resolve authorized inputs,
- construct retrieval query when specification permits,
- invoke professional adapter,
- stage/extract outputs,
- request authorized pointer mutations.

The handler may not:

- add undeclared outputs,
- widen retrieval scope,
- change lifecycle,
- route the Job,
- mutate undeclared pointers,
- change professional role binding.

---

# 21. Operation-by-Lifecycle Compatibility

Canonical:

```text
analysis
→ generate_analysis

evidence_request
→ request_evidence

investigation
→ investigate_evidence_request

evidence_integration
→ integrate_evidence

resume_production
→ generate_resume

evaluation
→ evaluate_resume
```

No professional operation executes outside its allowed lifecycle unless the specification is deliberately changed.

---

# 22. Known Planning Gap — `integrate_evidence` Task Resource

The architecture includes:

```text
integrate_evidence
```

as a V0.1 operation.

Implementation requires one exact approved professional task resource.

If the current repository lacks:

```text
agents/researcher/tasks/integrate-evidence.md
```

or equivalent approved instructions, this must be resolved before implementing the real professional invoker for that operation.

Allowed resolution paths:

```text
1. confirm an existing Researcher task already defines integration behavior;
2. add an explicit approved integration task;
3. revise the effective specification only after architecture/professional-contract review.
```

Do not invent hidden integration instructions inside Python handler code.

This is an implementation readiness dependency, not a reason to redesign orchestration.

---

# 23. Initial Registry Representation

Recommended conceptual Python:

```python
OPERATION_SPECIFICATIONS = {
    OperationType.GENERATE_ANALYSIS: OperationSpecification(...),
    OperationType.REQUEST_EVIDENCE: OperationSpecification(...),
    OperationType.INVESTIGATE_EVIDENCE_REQUEST: OperationSpecification(...),
    OperationType.INTEGRATE_EVIDENCE: OperationSpecification(...),
    OperationType.GENERATE_RESUME: OperationSpecification(...),
    OperationType.EVALUATE_RESUME: OperationSpecification(...),
}
```

or equivalent immutable YAML definitions loaded at startup.

The registry loader computes:

```text
operation_specification_hash
operation_registry_hash
```

after validation.

---

# 24. Fake Professional Invoker Fixtures

For implementation Slice 1, fake outputs should satisfy the same output contracts.

Example:

```text
generate_analysis
→ deterministic fixture JEA
```

Later fixtures:

```text
request_evidence
→ deterministic ERQ

generate_resume
→ deterministic Resume + WCM

evaluate_resume
→ deterministic Evaluation

investigate_evidence_request
→ deterministic ConversationTurn / Evidence Response

integrate_evidence
→ deterministic new JER version(s)
```

Fake behavior must not bypass schemas or Commit Coordinator.

---

# 25. Operation Conformance Tests

For every Operation Specification:

```text
valid lifecycle
→ handler can schedule

invalid lifecycle
→ rejected

required input missing
→ no Execution/provider invocation

undeclared input requested by handler
→ rejected

required retrieval fails
→ no professional invocation

required retrieval returns zero matches
→ professional invocation may proceed with valid empty result

output missing
→ commit rejected

schema invalid
→ commit rejected

unauthorized pointer mutation
→ commit rejected

freshness changed
→ staged output cannot become current

same identity dependencies
→ same logical operation_key

material identity dependency changed
→ different operation_key
```

---

# 26. Phase 6 Decisions Made

This phase establishes:

1. Six V0.1 professional operations have explicit specification definitions.
2. Each operation has exactly one lifecycle compatibility set.
3. Researcher analysis is the only operation currently expected to require broad reusable-evidence retrieval.
4. Writer and Evaluator do not independently expand evidence retrieval.
5. Resume + WCM is a coupled professional product.
6. Evidence integration is a coupled multi-JER/consumed-response commit.
7. Completed Interviewer Evidence Response commits with exact human-message consumption.
8. Mutation authority is operation-specific and minimal.
9. semantic specification identity includes material resource identities but not incidental Git SHA.
10. `integrate_evidence` requires confirmation of an exact approved professional task resource before real invocation implementation.

---

# 27. Open Decisions for Later Phases

Still unresolved:

- exact serialized specification format;
- exact retry policy values;
- exact `integrate_evidence` approved task resource;
- whether integration retrieval is `none` or `optional`;
- exact Resume file-format validator;
- whether `request_evidence` produces one or multiple ERQs per Execution;
- whether existing active ERQ reconciliation occurs during request_evidence commit or only during later deterministic reconciliation;
- exact resource list for each professional role after final repository inspection.

These should be turned into implementation backlog items where needed.

---

# 28. Phase 6 Acceptance Criteria

The Operation Specification Definitions are complete when:

- [ ] all six current professional operations have one explicit specification;
- [ ] each specification declares lifecycle compatibility;
- [ ] each specification declares required/optional inputs;
- [ ] identity and freshness dependencies are separated;
- [ ] retrieval authority is explicit;
- [ ] required outputs are explicit;
- [ ] coupled output groups are explicit;
- [ ] exact schema bindings are identified;
- [ ] pointer/collection mutation authority is minimal and explicit;
- [ ] handler key and professional binding are distinct;
- [ ] retry policy reference exists;
- [ ] registry validation requirements are explicit;
- [ ] specification hashing excludes incidental Git revision;
- [ ] no operation relies on handler-hidden professional rules;
- [ ] the `integrate_evidence` professional-task dependency is explicitly identified.

## Result

**READY FOR PHASE 7 — IMPLEMENTATION DEPENDENCY GRAPH**