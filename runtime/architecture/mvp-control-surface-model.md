# RRS V3 MVP Control Surface Model

## Status

Draft V0.1

## Purpose

The MVP Control Surface Model defines the minimum human-operable interface required to create, inspect, retry, review, and cancel Runtime Jobs before Trello or a web UI is implemented.

V0.1 standardizes on:

```text
CLI-first control surface
+
runtime Commands
+
read-only status inspection by default
```

The CLI is an operator interface, not a source of runtime or professional truth.

It must not bypass the Runtime Job, Event, Command, Handler, Routing, or Persistence models.

---

# Core Invariants

1. The CLI is a control surface, not the runtime architecture.
2. CLI write actions issue runtime Commands; they do not mutate SQLite tables directly.
3. CLI read actions use repository/service interfaces rather than raw database access.
4. Job creation follows the same Event/Command path future UIs will use.
5. Runtime Job state remains authoritative.
6. Professional artifact stores remain authoritative for professional content.
7. Retry targets recoverable runtime work; it does not blindly re-run professional agents.
8. Cancel is explicit and terminal in V0.1.
9. Manual Review exposes diagnostic state but does not perform professional reasoning.
10. CLI behavior must remain replaceable by HTTP, Trello, or another interface without changing runtime semantics.
11. Secrets are not accepted through unsafe CLI arguments when avoidable.
12. Human-readable output may summarize runtime state but must preserve exact IDs and versions needed for audit.

---

# 1. MVP Control Surface Scope

The V0.1 control surface must support:

```text
create job
show job
list jobs
show current artifacts
retry recoverable work
cancel job
inspect manual review state
```

Optional convenience commands may be added later.

The MVP does not require:

- Trello.
- Web UI.
- REST API.
- Job editing through Discord.
- Drag-and-drop routing.
- Direct artifact mutation through CLI.
- Direct lifecycle reassignment.
- Direct SQL access by operators.

---

# 2. CLI Command Shape

Recommended command namespace:

```bash
rrs job create ...
rrs job show JOB-0001
rrs job list
rrs job artifacts JOB-0001
rrs job retry JOB-0001
rrs job cancel JOB-0001
rrs job review JOB-0001
```

Additional implementation-specific subcommands may exist, but the conceptual surface should remain small.

---

# 3. Control Flow

All mutating CLI actions follow:

```text
CLI
 ↓
validate user input
 ↓
create Runtime Command
 ↓
persist Command
 ↓
runtime processes Command
 ↓
handlers/router mutate authoritative state
 ↓
CLI reports resulting state
```

Never:

```text
CLI
 ↓
direct UPDATE runtime_jobs
```

or:

```text
CLI
 ↓
direct artifact overwrite
```

---

# 4. Read Flow

Read-only commands follow:

```text
CLI
 ↓
runtime query/service
 ↓
repositories
 ↓
authoritative Runtime Job / metadata
 ↓
human-readable output
```

The CLI should not need to understand SQLite table layout.

---

# 5. `rrs job create`

## Purpose

Create a new Runtime Job and persist its initial professional state.

Example:

```bash
rrs job create --target-job ./brooks-job.pdf
```

Possible future inputs:

```bash
rrs job create \
  --target-job ./job.pdf \
  --label "Brooks IT Service Desk Manager"
```

The operator-facing label is optional runtime metadata and must not replace the target artifact.

---

# 6. Job Creation Semantics

Conceptual flow:

```text
accept Target Job source
↓
persist Target Job artifact
↓
resolve current reusable evidence baseline
↓
create Runtime Job
↓
Runtime Job lifecycle = new
↓
emit job_created Event
↓
schedule/evaluate initial routing
↓
analysis begins
```

The CLI should not directly call `generate_analysis`.

Job creation should enter the same runtime path future integrations use.

---

# 7. Target Job Input

The MVP should support at least one straightforward Target Job input mechanism.

Recommended first implementation:

```text
local file path
```

Supported artifact formats may include:

```text
PDF
plain text
Markdown
```

Additional URL/browser ingestion can be added later.

The Target Job must become a persisted professional/input artifact before professional operations consume it.

---

# 8. Reusable Professional Evidence on Job Creation

The Runtime Job should reference the current reusable professional evidence set required by the professional architecture.

Current model:

```text
JER set
```

Future Analyst/Custodian architecture may change how this reference is resolved.

The CLI should not require the operator to manually enumerate every JER.

A runtime service should resolve the current evidence baseline.

---

# 9. Create Result

On successful creation, the CLI should return:

```text
Created JOB-0001
Target: Brooks Running — IT Service Desk Manager
Phase: new
Health: healthy
```

and may briefly wait/report the first queued transition when practical.

The authoritative Job ID must always be visible.

---

# 10. `rrs job show`

## Purpose

Show current Runtime Job state without dumping all professional content.

Example:

```bash
rrs job show JOB-0001
```

Recommended output:

```text
JOB-0001
Target: Brooks Running — IT Service Desk Manager

Lifecycle: investigation
Health: healthy

Operation:
  status: idle
  type: —

Interaction:
  status: active
  id: INT-0004

Current professional state:
  Target Job: TARGET-0001 v1
  JEA: JEA-0004 v3
  Active ERQs: 2
  Unintegrated Evidence Responses: 0
  Resume: —
  WCM: —
  Evaluation: —

Updated: 2026-08-23T11:00:00-07:00
```

Exact field labels may vary.

---

# 11. `rrs job list`

## Purpose

Show Runtime Jobs at a glance.

Example:

```bash
rrs job list
```

Recommended columns:

```text
JOB ID
Target
Phase
Health
Operation
Interaction
Updated
```

Optional filters:

```bash
rrs job list --active
rrs job list --phase manual_review
rrs job list --health blocked
rrs job list --completed
```

V0.1 can implement only `--active` if scope needs to remain small.

---

# 12. Active Job Definition

Recommended V0.1 definition:

```text
lifecycle not in:
complete
cancelled
```

A Job in Manual Review remains active.

---

# 13. `rrs job artifacts`

## Purpose

Show exact current professional artifact pointers.

Example:

```bash
rrs job artifacts JOB-0001
```

Recommended output:

```text
Target Job
  TARGET-0001 v1
  artifacts/TARGET-0001/v1.pdf

Current JER Set
  JER-0001 v4
  JER-0007 v3
  ...

JEA
  JEA-0004 v5

Active ERQs
  ERQ-0011 v1
  ERQ-0012 v1

Unintegrated Evidence Responses
  none

Resume
  RESUME-0003 v4

WCM
  WCM-0003 v4

Evaluation
  EVAL-0003 v2
```

This command exposes references, not all artifact bodies.

---

# 14. Artifact Inspection

A future convenience command may support:

```bash
rrs artifact show JEA-0004 --version 5
```

or:

```bash
rrs artifact path RESUME-0003 --version 4
```

This is useful but not mandatory for the first MVP control surface.

The Artifact Store remains authoritative.

---

# 15. `rrs job retry`

## Purpose

Request safe retry/recovery of recoverable runtime work.

Example:

```bash
rrs job retry JOB-0001
```

The CLI must not simply re-run the last agent invocation.

---

# 16. Retry Semantics

Conceptual flow:

```text
operator requests retry
↓
retry_requested Command/Event
↓
runtime inspects:
  Job health
  active/failed Execution
  failure class
  operation key
  current professional state
↓
runtime selects safe retry/reconciliation path
```

Possible outcomes:

```text
new Execution attempt created
existing committed result reused
stale operation replaced by new logical operation
projection-only retry scheduled
retry rejected because manual recovery is required
```

The CLI reports the result.

---

# 17. Retry Eligibility

Normal retry should target:

```text
recoverable_failure
```

and explicitly retryable Execution/Event/Command states.

For:

```text
health == blocked
```

`rrs job retry` may be rejected unless runtime policy identifies a safe retry.

The operator should then use:

```bash
rrs job review JOB-0001
```

---

# 18. Retry Example

```text
JOB-0001

Health:
recoverable_failure

Failure:
EXEC-0042
invocation_failure
attempt 1 of 3

$ rrs job retry JOB-0001

Retry scheduled:
EXEC-0043
operation: generate_resume
logical operation: OPKEY-ABC
```

---

# 19. `rrs job cancel`

## Purpose

Explicitly terminate a Runtime Job.

Example:

```bash
rrs job cancel JOB-0001
```

V0.1 treats cancellation as terminal.

---

# 20. Cancellation Confirmation

Cancellation is destructive to workflow progression, so the CLI should request confirmation interactively where possible.

Example:

```text
Cancel JOB-0001?
This stops automatic processing and cannot be automatically reopened in V0.1.
[y/N]
```

Automation may provide:

```bash
--yes
```

for explicit noninteractive use.

---

# 21. Cancellation Semantics

Flow:

```text
cancel requested
↓
persist cancel Command
↓
runtime verifies Job is nonterminal
↓
stop/supersede safe active work
↓
lifecycle → cancelled
↓
emit job_cancelled
```

Cancellation does not delete:

- professional artifacts,
- execution history,
- events,
- interactions,
- routing history.

Historical state remains inspectable.

---

# 22. Cancelled Interaction

If a Job has an active Discord Interaction:

```text
Job cancellation
↓
Interaction → cancelled
↓
Discord thread may receive cancellation notice
↓
thread may be archived
```

The Discord projection failure must not invalidate Job cancellation.

---

# 23. `rrs job review`

## Purpose

Explain why automated processing entered Manual Review or is blocked.

Example:

```bash
rrs job review JOB-0001
```

Recommended output:

```text
JOB-0001 requires manual review.

Lifecycle: manual_review
Health: blocked

Reason:
  Resume Evaluation state is internally inconsistent.

Related runtime records:
  Execution: EXEC-0082
  Event: EVT-0144
  Failure: FAIL-0012

Current professional state:
  Evaluation: EVAL-0007 v2

Suggested runtime action:
  Inspect the referenced artifacts and failure records.
```

The CLI must not invent professional conclusions.

---

# 24. Manual Review Boundary

`job review` reports:

- runtime failure reason,
- failed invariant,
- relevant IDs,
- current pointer state,
- safe runtime actions if known.

It does not determine:

- whether evidence is truthful,
- whether the resume should say something else,
- whether a candidate qualifies,
- whether an agent made the correct professional judgment.

Those remain professional/governance concerns.

---

# 25. Future Manual Recovery Commands

V0.1 may initially support only:

```text
review
retry
cancel
```

Future safe recovery commands may include:

```text
resume
acknowledge
requeue-event
reconcile-execution
```

Do not add them until recovery semantics are well tested.

---

# 26. Control Surface Command Model

Mutating actions should use a generic runtime Command envelope.

Example:

```yaml
command:
  command_id: CMD-00042
  command_type: retry_execution
  job_id: JOB-0001
  created_at: ...
  source:
    type: cli
  payload:
    execution_id: EXEC-0042
```

The CLI may create commands through a Runtime Service rather than constructing raw command records itself.

---

# 27. CLI Source Identity

Commands created from CLI should record:

```text
source = cli
```

Optionally:

```text
operator identity
```

may be added later.

V0.1 is likely single-user and does not require a full RBAC model.

---

# 28. Exit Codes

The CLI should use meaningful process exit codes.

Conceptually:

```text
0 = success
1 = general/runtime error
2 = invalid arguments
3 = Job not found
4 = action rejected by runtime state
5 = recoverable operation failure
```

Exact codes may be finalized during implementation.

This helps shell scripting and Docker administration.

---

# 29. Machine-Readable Output

V0.1 should consider optional JSON output:

```bash
rrs job show JOB-0001 --json
```

This is useful for:

- scripts,
- tests,
- future HTTP wrapper,
- administration.

Human-readable output remains the default.

---

# 30. CLI Architecture Boundary

The CLI should call application/runtime services.

Conceptually:

```text
CLI command parser
↓
RuntimeControlService
↓
repositories / Command Store
```

Avoid embedding handler, router, or SQL behavior directly in CLI command functions.

---

# 31. Runtime Control Service

A thin application service may expose:

```python
class RuntimeControlService(Protocol):

    async def create_job(...):
        ...

    async def get_job(job_id):
        ...

    async def list_jobs(...):
        ...

    async def get_artifact_pointers(job_id):
        ...

    async def request_retry(job_id):
        ...

    async def request_cancel(job_id):
        ...

    async def get_manual_review(job_id):
        ...
```

The CLI becomes one adapter to this service.

A future HTTP API can reuse the same service.

---

# 32. Why Not Direct Repositories From CLI

Using a control service prevents the CLI from becoming coupled to:

- SQLite schema,
- filesystem layout,
- routing rules,
- retry rules,
- command persistence semantics.

The control surface remains replaceable.

---

# 33. Security

The CLI runs inside or alongside the trusted runtime environment.

V0.1 should still avoid exposing secrets through command-line arguments because process lists and shell history may capture them.

Use:

- environment variables,
- Docker secrets,
- config files with appropriate permissions.

Target Job paths and Job IDs are acceptable CLI arguments.

---

# 34. Docker Usage

The CLI may be exposed through the application container.

Examples:

```bash
docker exec rrs rrs job list
```

```bash
docker exec rrs rrs job show JOB-0001
```

Job creation may mount or copy target files into an accessible input path.

A future HTTP control API may improve convenience, but it is not required for MVP.

---

# 35. Example Docker Workflow

```bash
docker exec rrs rrs job create \
  --target-job /imports/brooks.pdf
```

Then:

```bash
docker exec rrs rrs job show JOB-0001
```

If evidence is needed, the human receives Discord investigation threads automatically.

Later:

```bash
docker exec rrs rrs job show JOB-0001
```

may report:

```text
Phase: complete
Resume: RESUME-0003 v4
Evaluation: EVAL-0003 v2
```

---

# 36. Job Completion Output

When a Job completes, `job show` should make the final products obvious.

Example:

```text
JOB-0001
Lifecycle: complete
Health: healthy

Final product:
  Resume: RESUME-0003 v4
  WCM: WCM-0003 v4
  Evaluation: EVAL-0003 v2

Submission readiness: ready_to_submit
```

The readiness value is read from the committed professional Evaluation, not recomputed by the CLI.

---

# 37. Artifact File Retrieval

For Docker usability, a future command should likely support:

```bash
rrs artifact export RESUME-0003 --version 4 --output /exports/
```

or similar.

This is useful but not required to establish initial runtime control.

The MVP may initially rely on the persistent artifact filesystem directly.

---

# 38. No Direct Lifecycle Command

V0.1 should not support commands like:

```bash
rrs job phase JOB-0001 resume_production
```

Lifecycle is derived by routing.

Allowing arbitrary manual phase mutation would bypass the professional state machine.

Manual Review recovery should use explicit recovery commands with validated semantics.

---

# 39. No Direct Pointer Mutation

V0.1 should not support:

```bash
rrs job set-jea JOB-0001 JEA-0004:v7
```

or equivalent.

Current pointer changes belong to commit/recovery machinery.

If manual pointer recovery becomes necessary, it should be a dedicated audited maintenance tool, not ordinary CLI functionality.

---

# 40. No Direct Professional Artifact Editing

The control surface does not edit:

- JERs,
- JEA,
- ERQs,
- Evidence Responses,
- Resume,
- WCM,
- Evaluation.

Professional state changes flow through professional operations and artifact versioning.

---

# 41. Logging

CLI output and runtime logs are distinct.

CLI should provide concise action results.

Runtime logs retain detailed execution/Event information.

Avoid printing sensitive full professional content by default.

---

# 42. CLI Error Example

```text
$ rrs job retry JOB-0001

Retry rejected.

JOB-0001 is blocked in manual_review.
Failure: FAIL-0012
Execution: EXEC-0082

Run:
  rrs job review JOB-0001
```

This is more useful than a Python traceback.

Debug mode may expose additional technical detail.

---

# 43. Job Not Found

Example:

```text
$ rrs job show JOB-9999

Job not found: JOB-9999
```

No automatic fuzzy matching should occur for authoritative IDs.

---

# 44. MVP Test Requirements

Control surface tests should include:

```text
create Job
→ persisted Job + Target artifact + job_created Event

show Job
→ accurate current Runtime Job state

list Jobs
→ terminal/nonterminal filtering

retry recoverable failure
→ safe retry Command

retry committed operation
→ no duplicate professional work

cancel active Job
→ terminal cancelled state

cancel completed Job
→ rejected

review blocked Job
→ correct diagnostic references

artifacts command
→ exact current pointers

no CLI command directly mutates professional artifact content

no CLI command directly sets lifecycle phase
```

---

# 45. V0.1 Acceptance Criteria

- [ ] MVP can operate without Trello.
- [ ] CLI can create a Runtime Job.
- [ ] Job creation persists Target Job state before processing.
- [ ] Job creation enters normal Event/Command/routing flow.
- [ ] CLI can show current Job lifecycle/health/operation/interaction state.
- [ ] CLI can list Jobs.
- [ ] CLI can show exact current artifact pointers.
- [ ] CLI can request safe retry.
- [ ] Retry does not blindly re-run agents.
- [ ] CLI can explicitly cancel a Job.
- [ ] Cancellation preserves historical artifacts/runtime records.
- [ ] CLI can inspect Manual Review state.
- [ ] CLI does not perform professional reasoning.
- [ ] CLI does not directly modify Runtime Job lifecycle.
- [ ] CLI does not directly modify current professional pointers.
- [ ] CLI does not edit professional artifacts.
- [ ] Mutating actions issue durable runtime Commands.
- [ ] Read actions use runtime services/repositories.
- [ ] Human-readable output preserves exact IDs/versions.
- [ ] Optional machine-readable output can be added without redesign.
- [ ] CLI can run conveniently inside the Docker deployment.
- [ ] A future HTTP/Trello control surface can reuse the same Runtime Control Service.

---

# Next Design Step

After this model is accepted, the remaining MVP architecture should focus on:

> **Professional Invocation Model**

That model should define how the runtime programmatically invokes V2/V3 professional agents, supplies contracts/tasks/artifacts, receives structured outputs, handles conversational Interviewer continuation, and records exact model/invocation provenance without coupling handlers to a specific model provider.