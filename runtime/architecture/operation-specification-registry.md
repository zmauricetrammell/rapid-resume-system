# RRS V3 Operation Specification Registry Model

## Status
Draft V0.1 — FIX-031

## Purpose

The Operation Specification Registry Model defines the declarative runtime contract for professional operations.

It separates:

```text
what an operation requires and permits
```

from:

```text
how its Python handler executes that operation
```

Handlers implement execution mechanics. Operation Specifications declare runtime and professional-operation semantics.

## Core Invariants

1. Runtime dispatch remains keyed by `operation_type`.
2. Every professional `operation_type` has exactly one effective Operation Specification in a runtime build.
3. Operation Specifications are declarative runtime configuration, not professional artifacts.
4. Handler classes do not own professional role identity, resource paths, schemas, lifecycle permissions, retrieval policy, or pointer authority.
5. Handlers consume an already-resolved immutable Operation Specification.
6. Operation Specifications are immutable for one Execution.
7. Specification identity participates in operation identity and Invocation provenance.
8. Specification changes that can change professional output must change logical operation identity.
9. Pointer authority belongs to the operation specification, not the professional role name.
10. Professional-role bindings are replaceable without redesigning orchestration.
11. Invalid or incomplete specifications fail startup/configuration validation.
12. Runtime code must not infer missing operation semantics from folder layout or agent names.

---

# 1. Registry Responsibility

The registry answers:

```text
Given operation_type,
what are the exact runtime semantics for this operation?
```

Conceptually:

```python
spec = operation_registry.get(OperationType.GENERATE_ANALYSIS)
```

The registry does not execute professional work.

It provides immutable configuration to:
- Command scheduling.
- OperationHandlers.
- Input resolvers.
- Invocation Bundle construction.
- Resource/schema loading.
- Commit authorization.
- Lifecycle validation.
- Idempotency/freshness calculation.
- Audit/provenance.

---

# 2. Operation Specification

Recommended conceptual shape:

```yaml
operation:
  operation_type: generate_resume

  handler_key: generate_resume

  allowed_lifecycle_phases:
    - resume_production

  professional_binding:
    professional_role: writer
    contract: agents/writer/contract.md
    task: agents/writer/tasks/generate-resume.md

  inputs:
    required:
      - target_job
      - job_experience_analysis
      - resume_skeleton
      - prompt_bank

    optional:
      - resume_evaluation

    identity_dependencies:
      - target_job
      - job_experience_analysis
      - resume_evaluation
      - resume_skeleton
      - prompt_bank
      - professional_binding
      - output_contract

    freshness_dependencies:
      - target_job
      - job_experience_analysis
      - resume_evaluation

  retrieval:
    requirement: none
    evidence_source: null

  outputs:
    required:
      - targeted_resume
      - writer_content_manifest

    coupled_groups:
      - [targeted_resume, writer_content_manifest]

  output_contract:
    schemas:
      - schemas/writer-content-manifest.yaml

  pointer_authority:
    - resume
    - wcm

  deterministic_reconciliation: []

  retry_policy_ref: professional_default
```

Exact serialization may be YAML, immutable Python definitions, or another deterministic form.

---

# 3. Registry vs Handler Registry

V3 has two distinct registries.

## Operation Specification Registry

Answers:

```text
What does this operation require and permit?
```

## Handler Registry

Answers:

```text
Which Python implementation executes it?
```

Canonical flow:

```text
command.operation_type
        ↓
Operation Specification Registry
        ↓
resolved OperationSpecification
        ↓
Handler Registry
        ↓
OperationHandler.execute(specification, ...)
```

---

# 4. Handler Key

`handler_key` selects the Python implementation strategy.

It is separate from:

```text
professional_role
```

Example:

```text
generate_analysis
→ handler_key = generate_analysis
→ professional_role = researcher
```

Later:

```text
generate_analysis
→ same compatible handler_key
→ professional_role = analyst
```

if operation semantics remain compatible.

---

# 5. Professional Binding

Professional binding resolves the professional resource set.

Example:

```yaml
professional_binding:
  professional_role: researcher
  contract: agents/researcher/contract.md
  task: agents/researcher/tasks/generate-analysis.md
```

Current V2-compatible bindings are provisional.

The runtime does not assume:

```text
generate_analysis == Researcher forever
```

---

# 6. Input Declarations

Specifications declare:
- required inputs,
- optional inputs,
- identity dependencies,
- freshness dependencies.

The Input Resolver may resolve only authorized inputs.

Missing required inputs prevent invocation.

The professional agent cannot expand the specification by requesting arbitrary runtime state.

---

# 7. Retrieval Declaration

Retrieval is explicit:

```yaml
retrieval:
  requirement: required
  evidence_source: configured
```

Allowed values:

```text
none
optional
required
```

Required retrieval failure prevents professional invocation.

Optional retrieval may be skipped only because the specification explicitly permits it.

---

# 8. Output Contract

Specifications declare all required outputs and coupled groups.

Example:

```yaml
outputs:
  required:
    - targeted_resume
    - writer_content_manifest

  coupled_groups:
    - [targeted_resume, writer_content_manifest]
```

Missing required outputs fail before commit.

---

# 9. Pointer Authority

Pointer mutation authority is declarative:

```yaml
pointer_authority:
  - resume
  - wcm
```

The Commit Coordinator verifies requested mutations against the resolved specification.

Professional role identity itself grants no pointer authority.

---

# 10. Lifecycle Authority

Allowed lifecycle phases are declarative.

The handler rejects execution outside those phases and does not repair lifecycle silently.

---

# 11. Deterministic Reconciliation

Specifications may name deterministic reconciliation functions.

Example:

```yaml
deterministic_reconciliation:
  - reconcile_active_erqs_from_jea
```

These functions:
- use only explicit structured state,
- contain no professional reasoning,
- are separately testable,
- cannot exceed pointer authority.

---

# 12. Specification Identity

Each effective specification receives immutable identity.

Recommended inputs:

```text
operation_type
canonical specification content
resolved resource references
runtime Git/build identity
```

Conceptually:

```text
operation_specification_hash = sha256(canonical_specification)
```

Execution provenance records the hash and build identity.

Material specification changes participate in logical operation identity.

---

# 13. Startup Validation

Before runtime readiness, validate:
- unique `operation_type`,
- resolvable `handler_key`,
- referenced resources exist,
- schemas parse,
- lifecycle values are valid,
- pointer fields are valid,
- output types are valid,
- coupled groups reference declared outputs,
- retrieval requirement is valid,
- dependencies reference authorized inputs/resources,
- professional binding resolves,
- reconciliation names resolve.

Failure means:

```text
runtime configuration invalid
→ do not mark runtime ready
```

---

# 14. Current V2-Compatible Registry

Current operation set:

```text
generate_analysis
request_evidence
investigate_evidence_request
integrate_evidence
generate_resume
evaluate_resume
```

Current bindings may remain:

```text
generate_analysis → researcher
request_evidence → researcher
integrate_evidence → researcher
investigate_evidence_request → interviewer
generate_resume → writer
evaluate_resume → evaluator
```

These are compatibility bindings, not permanent architecture.

---

# 15. Analyst / Custodian Migration

The future split may use:

## Rebinding

```text
generate_analysis:
  researcher → analyst
```

when semantics remain materially compatible.

## New Operations

```text
analyze_target
request_information
retrieve_evidence
integrate_evidence
```

when the domain split creates materially different actions.

The orchestration framework remains stable either way.

---

# 16. Suggested Repository Location

Architecture document:

```text
runtime/architecture/operation-specification-registry-model.md
```

Implementation may later use:

```text
runtime/
├── operations/
│   ├── registry.py
│   └── specifications/
│       ├── generate_analysis.yaml
│       ├── request_evidence.yaml
│       ├── investigate_evidence_request.yaml
│       ├── integrate_evidence.yaml
│       ├── generate_resume.yaml
│       └── evaluate_resume.yaml
```

Separate YAML files are not required for MVP if immutable Python-native definitions are simpler.

---

# 17. Testing Requirements

Required tests include:

```text
duplicate operation_type
→ startup failure

unknown handler_key
→ startup failure

missing required schema/resource
→ startup failure

handler requests undeclared pointer mutation
→ commit rejected

required input missing
→ invocation rejected

required retrieval unavailable
→ professional invocation not started

material specification changes
→ changed operation identity/provenance

generate_analysis rebound researcher → analyst
→ orchestration framework unchanged
```

---

# 18. V0.1 Acceptance Criteria

- [ ] Every professional operation has one effective declarative specification.
- [ ] Operation specification and Python handler implementation are distinct concepts.
- [ ] Handler Registry and Operation Specification Registry have separate responsibilities.
- [ ] Specifications declare lifecycle, inputs, dependencies, retrieval, outputs, schemas/resources, pointer authority, and professional binding.
- [ ] Handlers cannot expand specification authority.
- [ ] Specification identity is recorded in Execution/Invocation provenance.
- [ ] Invalid registry configuration prevents runtime readiness.
- [ ] Current V2 professional bindings are explicitly provisional.
- [ ] Analyst/Custodian migration can rebind or introduce operations without redesigning orchestration.