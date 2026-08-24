# RRS V3 Professional Invocation Model

## Status
Draft V0.7 — FIX-029, FIX-030, FIX-032, FIX-035, and FIX-037 applied; supplemental Operation Specification Registry alignment retained; FIX-040 and FIX-045 applied

## Purpose
The Professional Invocation Model defines how the V3 runtime programmatically invokes professional AI operations while preserving authority boundaries, reproducibility, portability, and provider independence.

The runtime decides which operation must occur, which exact inputs/resources are authorized, which retrieval source may be used, which schemas apply, and how the invocation is recorded. The professional AI decides the professional answer.

Raw model output does not become authoritative professional state until it passes extraction, validation, freshness, persistence, and commit.

## Core Invariants

1. Professional invocation is operation-centric, not chat-session-centric.
2. Each invocation uses an immutable Invocation Bundle.
3. Contracts, tasks, schemas, templates, and other resources are explicitly resolved.
4. Professional artifacts and static resources are distinct input categories.
5. Input resolution enforces professional authority boundaries.
6. Professional reasoning invocations are closed-context.
7. Evidence retrieval may occur before invocation through an authorized runtime-managed `EvidenceSource`.
8. Models do not receive unrestricted storage access in MVP.
9. Retrieval results are normalized and fingerprinted before professional reasoning.
10. Google Drive is the preferred V0.1 external evidence source where applicable.
11. `EvidenceSource` is abstract so Drive can later be replaced by local filesystem, local RAG, vector search, or another provider.
12. Provider details are hidden behind a Professional Invoker abstraction.
13. Raw provider responses are never professional state.
14. Operation-specific Output Extractors identify required artifacts.
15. Schema validation is performed by V3 even when provider structured-output features are used.
16. Missing required artifacts make an invocation incomplete even if accompanying prose is useful.
17. Interviewer continuation reconstructs context from persisted conversation rather than provider session memory.
18. Logical retry behavior remains visible in Execution history.
19. Invocation provenance records exact model, resources, inputs, retrieval results, and runtime version.
20. Large-context retrieval complexity is handled by the evidence-retrieval layer rather than blindly uploading the whole corpus.
21. Tool/provider access may be introduced only through explicit runtime authorization.
22. If an operation declares an EvidenceSource as required, source unavailability is a recoverable operation failure; the runtime must not silently invoke the professional agent with incomplete retrieval.
23. Runtime dispatch is operation-centric; professional-role bindings are configuration/resource mappings, not permanent architectural ownership by the current V2 agent names.
24. Operation semantics are loaded from a first-class immutable Operation Specification Registry rather than inferred from handler classes.
25. Invocation provenance records both the exact operation specification hash and the validated registry/build identity that governed the Execution.
26. Evidence retrieval crosses provider boundaries only through provider-neutral `EvidenceQuery`, `EvidenceSearchResult`, and `RetrievedEvidenceItem` runtime types.
27. Interviewer continuation returns a typed union: `ConversationTurn` or `CompletedProfessionalArtifact`; ambiguous free-form return shape is not a valid continuation result.

## 1. Invocation Position in the Runtime

```text
Runtime Command
      ↓
Operation Handler
      ↓
Input Resolver
      ↓
optional EvidenceSource retrieval
      ↓
Invocation Bundle
      ↓
Professional Invoker
      ↓
AI Professional Operation
      ↓
RawProfessionalResponse
      ↓
Output Extractor
      ↓
Staged Artifacts
      ↓
Validation
      ↓
Freshness Check
      ↓
Commit
```

The Professional Invoker does not own routing, persistence, Runtime Job pointer mutation, schema authority, evidence custody, Trello, or Discord provider mechanics.

## 2. Operation-Centric Invocation

Current operations may include:

```text
generate_analysis
request_evidence
investigate_evidence_request
integrate_evidence
generate_resume
evaluate_resume
```

Future Analyst/Custodian operations may include:

```text
analyze_target
request_information
retrieve_evidence
integrate_evidence
generate_analysis
```

Dispatch remains based on `operation_type`.

## 3. Invocation Bundle

```yaml
invocation_bundle:
  invocation_id: INV-0042
  job_id: JOB-0001
  execution_id: EXEC-0042
  operation_type: generate_resume
  professional_role: writer

  instructions:
    contract_ref:
      path: agents/writer/contract.md
      git_commit: abc123
      content_hash: sha256:...
    task_ref:
      path: agents/writer/tasks/generate-resume.md
      git_commit: abc123
      content_hash: sha256:...

  professional_inputs:
    - artifact_ref

  retrieval_results: []

  resources:
    - resource_ref

  output_contract:
    expected_artifact_types:
      - targeted_resume
      - writer_content_manifest
    schema_refs:
      - path: schemas/writer-content-manifest.yaml
        git_commit: abc123
        content_hash: sha256:...

  invocation_metadata:
    created_at: ...
```

The bundle is immutable once execution begins.

## 4. Professional Artifacts vs Resources

Current V0.1 professional artifacts include:

```text
Target Job
JER
JEA
ERQ
Evidence Response
Resume
WCM
Resume Evaluation
Process Feedback
```

Future/deferred Analyst/Custodian professional artifact concepts include:

```text
Information Request
Information Response
```

Their classification as future professional artifacts does not create V0.1 Runtime Job pointers, lifecycle phases, routing predicates, handlers, or required schemas.

Resources include:

```text
agent contract
task instruction
schema
Resume Skeleton
Prompt Bank
shared architecture resources when explicitly required
```

These categories are versioned/fingerprinted separately.

## 5. Operation Specification

Every professional operation resolves one immutable Operation Specification from the Operation Specification Registry.

The specification declares:
- handler key,
- allowed lifecycle phases,
- professional binding,
- required/optional inputs,
- identity dependencies,
- freshness dependencies,
- retrieval requirement,
- required resources,
- expected outputs,
- coupled output groups,
- schemas,
- pointer authority,
- deterministic reconciliation,
- retry-policy reference.

The Python handler does not own these declarations.

Conceptually:

```python
spec = operation_specifications.get(operation_type)
handler = handlers.get(spec.handler_key)
result = await handler.execute(job_id, command, spec)
```

The effective specification is frozen into Execution/Invocation provenance before professional work begins.

Changing a material specification field changes operation identity when it can legitimately change professional output or commit behavior.

See:

```text
runtime/architecture/operation-specification-registry-model.md
```

## 6. Resource Identity

```yaml
resource_ref:
  path: agents/writer/contract.md
  git_commit: abc123...
  content_hash: sha256:...
```

Use the same pattern for contracts, tasks, schemas, skeletons, prompt banks, and shared resources.

## 7. Docker / Repository Provenance

The running container should be built from a known repository state.

Record:

```text
RRS version
Git commit SHA
Docker image version/tag
```

per runtime build or startup record.

## 8. Input Resolver Authority

The Input Resolver may load only inputs authorized for the operation.

Example Writer inputs:

```text
Target Job
JEA
Resume Skeleton
Prompt Bank
applicable Resume Evaluation
Writer contract/task/schema
```

Writer should not automatically receive all JERs, all Evidence Responses, Discord transcripts, or Custodian internals.

The model cannot request arbitrary runtime storage access in MVP.

## 9. Closed-Context Professional Reasoning

V0.1 uses closed, explicitly authorized context for reasoning operations.

Examples:

```text
Writer
Evaluator
Analyst
Interviewer
```

They do not autonomously query Drive, runtime DB, Trello, Discord, GitHub, or the web unless a future operation explicitly grants access.

## 10. Evidence Retrieval Exception

Evidence retrieval is a distinct runtime capability performed through an authorized source abstraction.

```python
class EvidenceSource(Protocol):
    async def search(
        self,
        query: EvidenceQuery,
    ) -> EvidenceSearchResult:
        ...
```

The reasoning model receives normalized retrieval results, not unrestricted direct storage access.

## 11. V0.1 Evidence Source

Preferred V0.1 source:

```text
Google Drive
```

The reusable professional-source corpus may remain in Drive rather than being uploaded in full on every invocation.

This reduces transfer volume, context use, token use, latency, and duplicated storage.

## 12. EvidenceSource Implementations

Potential implementations:

```text
GoogleDriveEvidenceSource
LocalFilesystemEvidenceSource
LocalIndexedEvidenceSource
VectorEvidenceSource
TestEvidenceSource
```

Higher-level operations depend on the normalized interface, not provider-specific connectors.

## 12.1 EvidenceSource Availability and Failure Semantics

An operation may declare evidence retrieval as:

```text
required
```

or:

```text
optional
```

This is an operation-specification decision, not a provider decision.

If retrieval is required and the configured EvidenceSource cannot produce a valid retrieval result because of:

- provider outage,
- authentication failure,
- authorization failure,
- connector/API unavailability,
- source timeout,
- unreadable provider response,
- required source not reachable,

the runtime must fail the professional operation before model invocation.

Canonical behavior:

```text
required EvidenceSource unavailable
→ do not construct a falsely complete Invocation Bundle
→ do not invoke professional agent
→ Execution records recoverable retrieval failure
→ normal retry policy applies
```

The runtime must never reinterpret provider failure as:

```text
no relevant evidence found
```

Those states are materially different.

A successful empty retrieval result is valid only when the EvidenceSource completed normally and explicitly returned no matches.

Recommended distinction:

```text
retrieval_succeeded_empty
retrieval_succeeded_with_results
retrieval_failed_unavailable
```

If retrieval is optional, the operation specification must explicitly authorize continuation without it. The Invocation Bundle must record that no retrieval result was supplied and why.

For the current Researcher-compatible evidence path, retrieval against the configured professional evidence corpus should be treated as required whenever the operation depends on corpus search for correctness.

## 13. Google Drive Access Boundary

Preferred:

```text
Researcher/Custodian retrieval operation
      ↓
GoogleDriveEvidenceSource
      ↓
normalized retrieval result
      ↓
professional reasoning invocation
```

Avoid long-term architecture where the model has unrestricted Drive access.

## 14. Transitional Researcher Support

Before the Analyst/Custodian split:

```text
GenerateAnalysisHandler
      ↓
Researcher Input Resolver
      ↓
EvidenceSource.search(...)
      ↓
selected evidence
      ↓
Invocation Bundle
      ↓
Researcher
```

After the split:

```text
RetrieveEvidenceHandler
      ↓
Custodian
      ↓
EvidenceSource
      ↓
Information Response
      ↓
Analyst
```

The source abstraction survives the refactor.

## 15. Provider-Neutral Evidence Retrieval Types

The EvidenceSource boundary uses three provider-neutral runtime types:

```text
EvidenceQuery
EvidenceSearchResult
RetrievedEvidenceItem
```

Provider adapters translate provider-specific APIs into these types before professional reasoning receives retrieval results.

### `EvidenceQuery`

```yaml
evidence_query:
  query_id: QUERY-0042
  purpose: "Find evidence relevant to service-desk leadership and SLA ownership."
  search_text: "service desk SLA vendor leadership"
  requested_evidence_types:
    - job_experience_record
    - source_document
  filters:
    source_scope: reusable_professional_evidence
    date_from: null
    date_to: null
  max_results: 20
```

Rules:
- `query_id` is runtime identity for this resolved query.
- `purpose` describes why retrieval is authorized.
- `search_text` is provider-neutral search intent.
- `requested_evidence_types` and `filters` are normalized runtime constraints.
- Provider-specific query syntax does not appear in the common type.

### `RetrievedEvidenceItem`

```yaml
retrieved_evidence_item:
  item_id: RETRIEVED-0007

  source_ref:
    source_type: google_drive
    source_item_id: "provider-stable-id"
    source_version: "provider-version-or-modified-identity"

  title: "Network Operations Report"
  media_type: application/pdf

  content:
    excerpt: "..."
    normalized_text_hash: sha256:...

  metadata:
    modified_at: ...
    logical_path: "Professional Evidence/Reports/..."
```

Rules:
- `item_id` is runtime retrieval identity, not provider identity.
- `source_ref` preserves enough stable source identity for provenance and change detection.
- `content.excerpt` contains only the selected content supplied downstream.
- `normalized_text_hash` fingerprints the supplied professional evidence content.
- Provider-specific metadata may be retained under normalized metadata only when useful for provenance; downstream professional operations must not depend on provider-specific fields.

### `EvidenceSearchResult`

```yaml
evidence_search_result:
  query_id: QUERY-0042
  status: succeeded

  items:
    - retrieved_evidence_item

  executed_at: ...
  source_adapter: google_drive
  result_fingerprint: sha256:...
```

Allowed status:

```text
succeeded
```

Provider failure does not produce an `EvidenceSearchResult` with an empty item list. It produces the recoverable retrieval failure defined by the EvidenceSource failure model.

A successful query may return:

```text
items: []
```

which means retrieval completed normally and found no matching evidence.

## 16. Retrieval Fingerprint Inputs

`EvidenceSearchResult.result_fingerprint` is deterministic from the normalized retrieval result supplied to professional reasoning.

Recommended canonical fingerprint inputs:

```text
query identity/content
ordered RetrievedEvidenceItem source identity
source version identity
normalized supplied-content hash
```

Provider request IDs, latency, pagination tokens, and other transport details do not affect the professional retrieval fingerprint unless they change the evidence content supplied.

Items should be canonicalized in stable source identity order before hashing so provider response ordering does not change logical operation identity.

## 17. Retrieval Provenance

Persist enough information to answer:

```text
What source was searched?
What query was used?
Which files/items were returned?
What versions were returned?
What exact content was supplied to the model?
```

## 18. Retrieval Fingerprint

The logical professional operation identity should include the retrieval result used for reasoning.

Conceptually:

```text
Information Request
+
retrieval result fingerprint
+
task/resource identity
=
logical professional operation identity
```

Do not rely only on the search query.

## 19. Retrieval Result Fingerprinting

Recommended fingerprint inputs:

```text
source type
source item ID
source item version / modified identity
content hash of supplied excerpt/content
```

Canonicalize and hash deterministically.

## 20. Retrieval Result Storage

Persist retrieval metadata such as:

```text
retrieval ID
query
provider/source
returned source refs
versions
content hashes
selected excerpts/content refs
timestamps
```

Large source bodies need not be duplicated unnecessarily if exact source/excerpt identity is preserved.

## 21. External Source Change

If Drive content changes for the same source ID, indicated by a new version/modified identity or content hash, the retrieval result changes and a new logical invocation may be required.

Committed professional artifacts remain immutable.

## 22. Provider Portability

If Drive becomes unavailable or the runtime moves to an internal model, replace:

```text
GoogleDriveEvidenceSource
```

with:

```text
LocalFilesystemEvidenceSource
```

or:

```text
LocalIndexedEvidenceSource
```

without changing the higher-level professional interface.

## 23. Input Assembly

Logical assembly order:

```text
PROFESSIONAL ROLE / CONTRACT
TASK
AUTHORIZED PROFESSIONAL INPUTS
AUTHORIZED RETRIEVAL RESULTS
PRESENTATION / SHARED RESOURCES
OUTPUT CONTRACT
```

Provider APIs may represent these differently, but logical content remains stable.

## 24. Professional Role Mapping

Runtime dispatch is based on:

```text
operation_type
```

not on a permanently encoded agent identity.

The runtime resolves a professional implementation for an operation from explicit operation/resource configuration.

Current V2-compatible mapping:

```text
generate_analysis
→ researcher

request_evidence
→ researcher

investigate_evidence_request
→ interviewer

integrate_evidence
→ researcher

generate_resume
→ writer

evaluate_resume
→ evaluator
```

This mapping exists only to run the currently stable V2 professional agents through the V3 runtime.

It is provisional.

The planned Analyst/Custodian decomposition may instead map operations such as:

```text
analyze_target
→ analyst

request_information
→ analyst

retrieve_evidence
→ custodian

integrate_evidence
→ custodian

generate_analysis
→ analyst

investigate_evidence_request
→ interviewer

generate_resume
→ writer

evaluate_resume
→ evaluator
```

The exact future operation vocabulary will be finalized by the Analyst/Custodian design issue.

The important architectural rule is:

```text
Command
→ operation_type
→ OperationHandler
→ operation specification
→ configured professional role/resources
```

not:

```text
Command
→ hard-coded Researcher/Writer/Evaluator class
```

Changing which professional role implements an operation must not require changing Command semantics, Runtime Job lifecycle semantics, Event vocabulary, or the common handler interface unless the operation itself changes.

Professional role mapping belongs in runtime operation specifications/configuration and is recorded in Invocation provenance.


## 25. Professional Invoker Interface

```python
class ProfessionalInvoker(Protocol):
    async def invoke(
        self,
        bundle: InvocationBundle,
    ) -> RawProfessionalResponse:
        ...
```

Possible implementations:

```text
OpenAIProfessionalInvoker
LocalModelProfessionalInvoker
TestProfessionalInvoker
```

## 26. Runtime Model Configuration

Provider/model selection belongs in runtime configuration.

Professional-role identity is also resolved through configuration/resources rather than being hard-coded into the orchestration framework.

Conceptually:

```yaml
operation_bindings:
  generate_analysis:
    professional_role: researcher
    contract: agents/researcher/contract.md
    task: agents/researcher/tasks/generate-analysis.md

  generate_resume:
    professional_role: writer
    contract: agents/writer/contract.md
    task: agents/writer/tasks/generate-resume.md
```

Provider selection may then be configured independently:

```yaml
professional_roles:
  researcher:
    provider: openai
    model: configured-model

  writer:
    provider: openai
    model: configured-model

  evaluator:
    provider: openai
    model: configured-model
```

After the Analyst/Custodian split, the operation binding may change without redesigning the runtime:

```yaml
operation_bindings:
  generate_analysis:
    professional_role: analyst
```

Professional contracts do not hard-code model identity, and orchestration code does not permanently hard-code V2 professional-role ownership.

## 27. Invocation Provenance

Each Execution should record exact provider, operation, resource, and runtime identity.

Recommended:

```yaml
invocation_provenance:
  invocation_id: INV-0042

  operation:
    operation_type: generate_resume
    operation_specification_hash: sha256:...
    operation_registry_hash: sha256:...

  runtime_build:
    git_sha: abc123...
    image_digest: sha256:...

  model_invocation:
    provider: openai
    model: configured-model
    provider_request_id: "..."
    started_at: ...
    completed_at: ...

    usage:
      input_tokens: ...
      output_tokens: ...

    latency_ms: ...

  resources:
    contract_hash: sha256:...
    task_hash: sha256:...
    schema_hashes:
      - sha256:...
```

Usage may be null when unavailable.

This provenance must make it possible to answer:

```text
Which exact operation rules governed this invocation?
Which runtime build loaded those rules?
Which professional resources and provider/model were used?
```

The registry/build identity is immutable for the Execution.

## 28. Raw Professional Response

Provider output enters as:

```text
RawProfessionalResponse
```

It may contain text, structured data, attachments/files, provider metadata, or continuation output.

It is not authoritative professional state.

## 29. Output Extractor

```python
class OutputExtractor(Protocol):
    def extract(
        self,
        response: RawProfessionalResponse,
    ) -> tuple[StagedArtifact, ...]:
        ...
```

Examples:

```text
GenerateAnalysisOutputExtractor
RequestEvidenceOutputExtractor
EvidenceResponseOutputExtractor
GenerateResumeOutputExtractor
EvaluationOutputExtractor
```

Extractors parse outputs; they do not judge professional correctness.

## 30. Required Output Enforcement

Examples:

```text
generate_analysis → JEA required
request_evidence → ERQ required
generate_resume → Resume + WCM required
evaluate_resume → Resume Evaluation required
```

If required output is missing, the invocation is incomplete and execution fails.

Useful prose does not substitute for required artifacts.

## 31. Human-Readable Commentary

Optional commentary may accompany authoritative artifacts. The runtime may retain it as Execution metadata/logging, but it does not become a professional artifact unless explicitly defined as one.

## 32. Schema Delivery

If conformance requires a schema, the exact schema supplied to the model must be the same schema used for runtime validation.

Invocation provenance records path, Git SHA, and content hash.

## 33. Provider Structured Output

Provider structured-output constraints may be used, but runtime schema validation still runs.

```text
provider validation
≠
authoritative runtime validation
```

## 34. Interviewer Continuation

Each continuation is reconstructed from persisted state and consumes one immutable ordered batch of human input.

Required input includes:

```text
exact ERQ
persisted ordered conversation
all currently unprocessed authorized human messages at batch resolution
Interviewer contract/task
Evidence Response schema
```

Continuation identity includes:

```text
interaction_id
current ERQ artifact ID + version
last prior persisted Interviewer turn boundary
ordered human message IDs in current batch
Interviewer task/contract/resource identity
```

Order the human-message batch by:

```text
provider_created_at ASC
provider_message_id ASC
```

Messages committed after batch resolution do not mutate the current Invocation Bundle and belong to the next continuation.

### Typed Continuation Result

The Interviewer must return exactly one member of this tagged union:

```text
InterviewerContinuationResult =
  ConversationTurn
  | CompletedProfessionalArtifact
```

`ConversationTurn`:

```yaml
kind: conversation_turn
message:
  content: "..."
  message_type: question
```

`CompletedProfessionalArtifact`:

```yaml
kind: completed_professional_artifact
artifact:
  artifact_type: evidence_response
  schema_version: ...
  content: ...
```

Rules:
- `kind` is required and unambiguous.
- `conversation_turn` means the investigation remains conversationally active.
- `completed_professional_artifact` means the professional candidate output enters normal extraction, schema validation, staging, freshness, and commit processing.
- For a completed Evidence Response, the exact immutable human-message batch in the Invocation Bundle must be durably marked processed in the same SQLite transaction that commits the professional artifact metadata/current-state mutation, finalizes the Execution, and persists `artifact_committed`.
- The returned artifact content is not authoritative merely because the Interviewer selected `completed_professional_artifact`.
- V0.1 allows only `evidence_response` as the completed professional artifact type for Interviewer investigation.
- Prose that appears to contain both a question and a completed Evidence Response is invalid until the Output Extractor can resolve exactly one union member.

This gives a stable logical boundary:

```text
same Interaction
+ same ERQ
+ same prior conversation boundary
+ same exact ordered human-message batch
→ same continuation input
```

No provider conversation/session memory is required for correctness.

## 35. Resume Generation

Current Writer may produce a Resume file + WCM.

Potential future improvement:

```text
AI-generated structured resume content
+
deterministic Python DOCX renderer
```

This would separate professional content reasoning from document mechanics, but does not block MVP.

## 36. Large Context Policy

V0.1 should not solve large corpora by sending every source file to every invocation.

Preferred:

```text
targeted EvidenceSource retrieval
→ normalized selected evidence
→ closed-context reasoning
```

If an invocation still exceeds context limits, fail safely rather than silently truncating authoritative input.

## 37. Retrieval and Analyst/Custodian

Future flow:

```text
Analyst
→ Information Request

Custodian
→ EvidenceSource retrieval
→ Information Response

Analyst
→ JEA
```

This naturally reduces context size.

## 38. Provider Timeouts

Professional invocations use configured runtime timeouts.

Timeout maps to:

```text
INVOCATION_FAILURE
```

and normal Execution retry behavior applies.

## 39. Retry Boundary

Transport-level retries inside a provider adapter should remain limited.

Logical professional retries belong to V3 and remain visible as Execution attempts.

## 40. Provider-Specific Settings

Settings such as temperature, reasoning effort, max output size, and tool configuration belong in provider/runtime configuration behind the adapter.

## 41. Invocation Security

The model cannot expand its own authority.

Examples:

```text
Writer asks for all JERs
→ runtime does not automatically provide them

Evaluator asks to search Drive
→ runtime does not grant access unless operation spec authorizes retrieval
```

## 42. Tool Access Policy

V0.1 default:

```text
no autonomous runtime/tool access inside professional reasoning invocations
```

Exception: explicit evidence-retrieval operations using runtime-managed `EvidenceSource` adapters.

Future tool access must be scoped by operation.

## 43. Google Drive Provider Caveat

Drive is a V0.1 evidence-source implementation choice, not a professional-agent architectural dependency.

If the OpenAI runtime exposes a suitable programmable Drive connector, the adapter may use it. Otherwise, the adapter may use the Google Drive API or another supported mechanism.

The professional operation interface remains unchanged.

## 44. Test Professional Invoker

Tests should use deterministic fake invokers.

```python
fake_invoker = TestProfessionalInvoker(
    response=known_valid_evaluation
)
```

This avoids live model dependencies when testing handler lifecycle, idempotency, commit logic, routing, stale detection, schema failure, or Discord state.

## 45. Test Evidence Source

```python
fake_source = TestEvidenceSource(
    results=known_evidence_result
)
```

This supports deterministic tests for retrieval fingerprints, provider portability, invocation construction, and future Analyst/Custodian behavior.

## 46. Invocation Audit Requirements

The runtime should be able to answer:

```text
Which operation produced this artifact?
Which professional role was invoked?
Which provider/model was used?
Which contract/task/schema versions were used?
Which professional artifacts were inputs?
Which retrieval result was used?
Which source files contributed evidence?
Which execution attempt committed the output?
```

## 47. Invocation Persistence

Invocation metadata may live inside Execution records or a dedicated Invocation table if later complexity justifies it.

V0.1 does not require a separate store if Execution records can capture the complete bundle/provenance.

## 48. Evidence Retrieval Persistence

Retrieval state may live in Execution metadata or a dedicated retrieval table.

It must preserve exact retrieval identity and fingerprints needed for reproducibility and stale/idempotency checks.

## 49. Operation-Key Integration

The logical operation key should incorporate:

```text
job ID
operation type
professional input snapshot
retrieval-result fingerprint where applicable
task identity
contract identity
semantically material schema/resource identity
```

Changed Drive evidence therefore changes logical invocation identity.

## 50. No Blind Corpus Upload

V0.1 explicitly avoids:

```text
load all professional files
→ send entire corpus on every invocation
```

unless a specific operation intentionally requires that behavior and context budget safely permits it.

## 51. Failure Classes

Invocation failures map to the existing runtime vocabulary:

```text
EVIDENCE_SOURCE_UNAVAILABLE

INVOCATION_FAILURE
OUTPUT_PARSE_FAILURE
SCHEMA_VALIDATION_FAILURE
CROSS_OUTPUT_VALIDATION_FAILURE
STALE_INPUT
```

A dedicated retrieval-failure class may be added later only if implementation evidence justifies it.


`EVIDENCE_SOURCE_UNAVAILABLE` is recoverable by default.

It means the runtime could not obtain required retrieval input from the configured EvidenceSource. It does not mean the corpus contained no relevant evidence.

The professional agent must not be invoked for that Execution unless required retrieval succeeds.

## 52. V0.1 Acceptance Criteria

- [ ] Evidence retrieval uses provider-neutral `EvidenceQuery`, `EvidenceSearchResult`, and `RetrievedEvidenceItem` types.
- [ ] Successful empty retrieval is distinguishable from EvidenceSource failure.
- [ ] Retrieval fingerprints are deterministic from normalized supplied evidence, not provider transport details.
- [ ] Interviewer continuation returns exactly one typed `ConversationTurn` or `CompletedProfessionalArtifact`.
- [ ] V0.1 `CompletedProfessionalArtifact` from Interviewer is restricted to Evidence Response and still requires normal professional commit processing.

- [ ] Invocation provenance records exact specification and registry/build identity.
- [ ] Registry/build identity is immutable for an Execution.
- [ ] A material operation-specification change is externally distinguishable in provenance.

- [ ] Operation Specification Registry is the authoritative declarative source for professional operation semantics.
- [ ] Professional invocation consumes a resolved immutable Operation Specification rather than handler-owned declarations.
- [ ] Material specification identity participates in operation identity/provenance.

- [ ] Runtime dispatch is operation-centric rather than permanently agent-centric.
- [ ] Current Researcher bindings are explicitly V2-compatible and provisional.
- [ ] Professional role/resource bindings are configuration-resolved and provenance-recorded.
- [ ] Future Analyst/Custodian rebinding can occur without redesigning the orchestration core.

- [ ] Interviewer continuation identity includes the exact ordered human-message batch.
- [ ] Later-arriving messages cannot mutate an already-resolved Invocation Bundle.

- [ ] Professional invocations are operation-centric.
- [ ] Every invocation uses an immutable Invocation Bundle.
- [ ] Contracts/tasks/schemas/resources are explicitly resolved.
- [ ] Resource identity includes reproducible version/hash metadata.
- [ ] Professional artifacts and static resources are distinguished.
- [ ] Input Resolver enforces professional authority boundaries.
- [ ] Professional reasoning invocations are closed-context.
- [ ] Evidence retrieval is supported through an authorized `EvidenceSource`.
- [ ] Google Drive can serve as the V0.1 source.
- [ ] Google Drive is not a permanent provider dependency.
- [ ] Local/filesystem/RAG source replacements remain possible.
- [ ] Retrieval results are normalized.
- [ ] Retrieval provenance and fingerprints are persisted.
- [ ] Changed source evidence changes logical invocation identity.
- [ ] Professional Invoker hides provider implementation.
- [ ] Model/provider configuration is runtime configuration.
- [ ] Raw provider output never directly becomes professional state.
- [ ] Operation-specific Output Extractors exist conceptually.
- [ ] Missing required artifacts cause invocation failure.
- [ ] Runtime independently validates authoritative schemas.
- [ ] Optional prose does not substitute for required artifacts.
- [ ] Interviewer continuation reconstructs from persisted interaction state.
- [ ] Logical retries remain visible in Execution history.
- [ ] Models cannot autonomously expand storage/tool authority.
- [ ] Large corpus transfer is minimized through retrieval.
- [ ] Invocation provenance supports end-to-end audit.
- [ ] Test invoker and test evidence source can replace live external dependencies.
- [ ] Planned Analyst/Custodian split can use the same invocation framework.

## Next Design Step

After this model is accepted, the final planned MVP architecture artifact should be the:

> **V3 MVP Runtime and Deployment Model**

It should define container process layout, worker/task loops, startup/shutdown, SQLite initialization, Discord adapter lifecycle, command/event processing, professional invocation workers, configuration, Docker volumes, health checks, restart recovery, and MVP deployment boundaries.