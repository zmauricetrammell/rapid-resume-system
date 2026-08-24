# Rapid Resume System

The **Rapid Resume System (RRS)** is a multi-agent system for producing
targeted, evidence-based resumes from a reusable body of professional
experience.

RRS separates professional reasoning from runtime orchestration.
Specialized AI roles analyze evidence, investigate factual gaps, write
resumes, evaluate the finished product, and govern the system, while a
deterministic runtime is responsible for state, routing, persistence,
retries, recovery, and human interaction.

The goal is to produce resumes that are:

-   Highly targeted to a specific job.
-   Grounded in confirmed professional evidence.
-   Traceable to source experience.
-   Written in recognizable civilian professional language.
-   Independently evaluated before submission.
-   Repeatable without reconstructing an entire career for every
    application.
-   Operable through a recoverable, auditable runtime rather than manual
    artifact handoffs.

> **Current status: V3 MVP Runtime Architecture --- CONFORMANCE PASS.**
>
> The professional reasoning architecture is established and the V3
> runtime architecture has completed its conformance audit. The project
> is entering **implementation planning**.
>
> V3 preserves the existing professional agents and artifacts while
> adding deterministic runtime orchestration around them.

------------------------------------------------------------------------

# Why This Exists

Writing a strong targeted resume involves several different kinds of
work:

1.  Understanding what an employer actually needs.
2.  Searching a large career history for relevant evidence.
3.  Determining how strongly that evidence supports each requirement.
4.  Identifying factual gaps in the professional record.
5.  Asking useful questions to recover undocumented experience.
6.  Translating unusual, specialized, or military experience into
    recognizable civilian professional functions.
7.  Selecting and presenting the strongest relevant evidence within
    limited resume space.
8.  Evaluating the finished resume from the perspective of an ATS,
    recruiter, and hiring manager.
9.  Repeating the process safely when evidence, analysis, or evaluation
    changes.

Trying to perform all of these functions inside one AI role creates
competing objectives and unclear authority. Trying to solve
orchestration by making the agents manage workflow creates a different
problem: professional reasoning becomes coupled to queues, retries,
routing, and transport.

RRS separates both concerns.

``` text
Professional reasoning
        │
        │ produces authoritative professional artifacts
        ▼
Deterministic runtime
        │
        │ persists state, routes work, recovers failures
        ▼
Next professional operation or human interaction
```

The professional agents decide matters within their professional
domains.

The runtime decides what work is eligible to run, when it runs, what
state changes are authorized, and how the system recovers when execution
is interrupted.

------------------------------------------------------------------------

# System Overview

RRS contains four production professional roles and one governance role:

``` text
Researcher
    Professional evidence and job analysis

Interviewer
    Human evidence investigation

Writer
    Resume presentation

Evaluator
    Independent resume evaluation

Supervisor
    System governance and continuous improvement
```

These agents are **professional roles, not workflow nodes**.

Agents do not need to know:

-   Which agent produced an input.
-   Which agent will consume an output.
-   How artifacts are transported.
-   What happens before or after their task.
-   What runtime workflow is being used.
-   How retries, persistence, routing, or recovery work.

V3 adds a runtime around those roles:

``` text
                    ┌──────────────────────┐
                    │      Runtime Job     │
                    │ authoritative state  │
                    └──────────┬───────────┘
                               │
                         deterministic
                            routing
                               │
                    ┌──────────▼───────────┐
                    │ Command / Execution  │
                    └──────────┬───────────┘
                               │
                    Operation Specification
                               │
                    ┌──────────▼───────────┐
                    │  Operation Handler   │
                    └──────────┬───────────┘
                               │
                    Professional Invocation
                               │
                 ┌─────────────▼─────────────┐
                 │ Researcher / Interviewer  │
                 │ Writer / Evaluator        │
                 └─────────────┬─────────────┘
                               │
                      professional output
                               │
                    ┌──────────▼───────────┐
                    │ Commit Coordinator   │
                    └──────────┬───────────┘
                               │
                      artifact_committed
                               │
                    ┌──────────▼───────────┐
                    │ Event → Command →    │
                    │ Router               │
                    └──────────────────────┘
```

The runtime orchestrates professional work without moving professional
judgment into the orchestration layer.

------------------------------------------------------------------------

# Professional Roles

## Researcher

The **Researcher** is the authoritative custodian of professional
evidence and job-fit analysis.

Its responsibilities include:

-   Analyzing target job descriptions.
-   Searching the complete professional evidence set.
-   Mapping job requirements to evidence.
-   Distinguishing direct, transferable, partial, and unsupported
    experience.
-   Maintaining authoritative professional evidence.
-   Reconciling new evidence with existing evidence.
-   Classifying supported civilian professional functions.
-   Determining evidence sufficiency.
-   Generating Job Experience Analyses.
-   Generating Evidence Requests when material factual questions remain
    unresolved.

The Researcher owns analytical judgment about professional evidence.

------------------------------------------------------------------------

## Interviewer

The **Interviewer** investigates factual questions with the human.

Given an Evidence Request, it conducts a collaborative investigation
designed to establish what actually happened.

Its responsibilities include:

-   Asking targeted, adaptive questions.
-   Helping the human recall relevant experiences.
-   Clarifying responsibility and decision authority.
-   Establishing scope and attribution.
-   Identifying relevant systems, methods, and tools.
-   Establishing results and outcomes.
-   Preserving uncertainty and negative evidence.
-   Producing an Evidence Response.

The Interviewer owns the quality of the factual investigation. It does
not classify evidence or determine job fit.

In V3, human investigation is mediated through a persistent
**Interaction** so an interrupted Discord conversation can be recovered
without losing authoritative state.

------------------------------------------------------------------------

## Writer

The **Writer** turns authorized professional evidence into a targeted
resume.

The Writer owns presentation.

Its responsibilities include:

-   Selecting authorized evidence for limited resume space.
-   Translating evidence into concise resume language.
-   Determining where evidence should appear.
-   Presenting supported professional functions clearly.
-   Translating unfamiliar experience into recognizable civilian
    terminology.
-   Balancing technical depth, leadership, scope, and results.
-   Aligning the resume with the target employer.
-   Preserving factual provenance and attribution.
-   Producing a Writer Content Manifest for traceability.

The Writer may reorganize supported experience for professional clarity.
It may not invent evidence or strengthen claims beyond what current
analysis supports.

------------------------------------------------------------------------

## Evaluator

The **Evaluator** independently judges the targeted resume as a hiring
product.

It evaluates the resume from the perspectives of:

-   Initial screening and ATS.
-   Recruiter review.
-   Hiring-manager review.

Its central question is:

> **Does the visible resume actually demonstrate what this employer
> needs?**

The Evaluator assesses requirement coverage, credibility, comprehension,
positioning, seniority, ATS alignment, screening risk, factual
integrity, and submission readiness.

The Evaluator owns the judgment that a product deficiency exists. It
does not rewrite the resume or redefine authoritative evidence.

------------------------------------------------------------------------

## Supervisor

The **Supervisor** governs the design of the system rather than
producing resumes.

Its responsibilities include:

-   Reviewing architecture.
-   Reviewing agent contracts and task instructions.
-   Reviewing schemas.
-   Identifying authority conflicts.
-   Identifying recurring process problems.
-   Analyzing Process Feedback.
-   Drafting proposed system improvements.
-   Supporting controlled refactoring and continuous improvement.

The human **System Owner** retains approval authority over changes to
the active architecture.

------------------------------------------------------------------------

# Separation of Authority

RRS assigns important decisions to explicit authorities.

  Domain                                      Authority
  ------------------------------------------- -------------------------
  Professional evidence and job analysis      Researcher
  Human factual investigation                 Interviewer
  Resume presentation                         Writer
  Resume evaluation                           Evaluator
  System architecture and governance          Supervisor
  Approval of system changes                  System Owner
  Professional-operation mutation authority   Operation Specification
  Professional artifact commit                Commit Coordinator
  Lifecycle and routing decisions             Router
  Detailed human-interaction state            Interaction Store
  Runtime persistence and CAS enforcement     Runtime repositories

Professional-role identity does not grant arbitrary runtime mutation
authority.

An **Operation Specification** declares what a professional operation
requires, what it may produce, when it may run, and what professional
state it may mutate. The runtime enforces that contract.

------------------------------------------------------------------------

# Professional Operations

Tasks represent **professional operations**, not workflow states.

Current production operations include:

``` text
Researcher
├── generate_analysis
└── request_evidence

Interviewer
└── investigate_evidence_request

Writer
└── generate_resume

Evaluator
└── evaluate_resume
```

V3 runtime operation specifications bind these professional operations
to their required inputs, resources, outputs, schemas, lifecycle
permissions, freshness dependencies, mutation authority, and handler
implementations.

Repeated execution uses current authoritative state rather than
requiring special workflow-specific variants such as `revise_resume` or
`reevaluate_resume`.

------------------------------------------------------------------------

# Professional Artifacts

Agents communicate professional state through explicit artifacts rather
than assumed shared memory.

Core V0.1 artifacts include:

-   **Target Job** --- the job being pursued.
-   **Job Experience Record (JER)** --- authoritative record of a
    professional episode.
-   **Job Experience Analysis (JEA)** --- analysis of evidence against
    the target job.
-   **Evidence Request (ERQ)** --- a material factual question requiring
    human investigation.
-   **Evidence Response** --- factual information established through
    investigation.
-   **Targeted Resume** --- the current application product.
-   **Writer Content Manifest (WCM)** --- traceability between resume
    content and authorized evidence.
-   **Resume Evaluation** --- independent assessment of the current
    resume.
-   **Process Feedback** --- observations about system-level friction or
    improvement opportunities.

Artifacts describe professional state. They do not encode runtime
destinations, queues, corrective ownership, or transport.

Future Analyst/Custodian concepts such as Information Request and
Information Response are intentionally deferred from the V0.1 runtime.

------------------------------------------------------------------------

# V3 Runtime Model

## Runtime Job

The **Runtime Job** is the authoritative runtime aggregate for one
resume-production job.

It tracks:

-   Lifecycle phase.
-   Current professional artifact pointers and collections.
-   Current operation state.
-   Coarse Interaction projection.
-   Runtime health.
-   Revision for compare-and-swap mutation.
-   Routing history and related control-plane state.

Runtime Job mutations use revision/CAS semantics to prevent silent lost
updates.

------------------------------------------------------------------------

## Operation Specifications

The **Operation Specification Registry** is the declarative contract
between professional architecture and runtime execution.

For each `operation_type`, the effective specification declares concepts
such as:

``` text
allowed lifecycle phases
required and optional inputs
identity dependencies
freshness dependencies
professional role binding
contract and task resources
retrieval requirements
required outputs
coupled output groups
output schemas
pointer/collection mutation authority
deterministic reconciliation
retry policy
handler key
```

Handlers implement execution mechanics. They do not invent
professional-operation authority.

Semantic Operation Specification identity is based on the effective
specification and material semantic resources. Git/build identity is
recorded separately as provenance.

------------------------------------------------------------------------

## Commands, Events, and Executions

V3 separates three different concepts.

**Commands** represent durable runtime work to be performed.

**Events** record meaningful committed runtime facts and trigger
deterministic follow-up work.

**Executions** represent physical attempts to perform professional
operations.

For example:

``` text
artifact_committed
        ↓
Event processor
        ↓
evaluate_routing Command
        ↓
Router
        ↓
lifecycle mutation
        ↓
lifecycle_changed
```

A short-lived Command lease never stands in for a long-running
professional provider call. The Execution owns the professional
invocation attempt and survives independently of the scheduling Command.

------------------------------------------------------------------------

## Professional Commit

Professional outputs do not become authoritative merely because a model
returned them.

The runtime stages and validates output before the **Commit
Coordinator** performs the authoritative commit.

Conceptually:

``` text
professional invocation
        ↓
candidate output
        ↓
schema / contract validation
        ↓
freshness validation
        ↓
immutable artifact finalization
        ↓
SQLite professional commit
    ├── artifact metadata
    ├── authorized Runtime Job mutation
    ├── Runtime Job revision
    ├── Execution finalization
    └── artifact_committed Event
```

`artifact_committed` is persisted by the Commit Coordinator inside the
authoritative professional commit transaction. It is the canonical
professional-state event used to trigger routing.

Coupled products such as the Targeted Resume and Writer Content Manifest
commit as a semantic group.

------------------------------------------------------------------------

## Persistence

V3 V0.1 uses:

``` text
SQLite
    authoritative runtime/control-plane state

Persistent filesystem
    immutable professional artifact content
```

SQLite stores Jobs, Commands, Events, Executions, Interactions,
Failures, artifact metadata, runtime/build identity, and related
control-plane state.

The filesystem cannot participate in SQLite ACID transactions. Artifact
files are therefore finalized before the authoritative SQLite commit.
Orphaned immutable files are tolerable; authoritative pointers to
incomplete files are not.

The V0.1 deployment assumes one active runtime container using one
SQLite database.

------------------------------------------------------------------------

## Human Interaction

Discord is the planned V0.1 human interaction surface for Evidence
Request investigation.

The runtime persists:

-   Interaction identity and status.
-   Discord thread/channel identity.
-   Provider message boundaries.
-   Authorized human messages.
-   Processed-message state.
-   Interviewer continuation state.

For ordinary conversational turns, the exact consumed human-message
batch and next Interviewer message are coordinated durably.

When an Interviewer continuation produces a completed Evidence Response,
the exact human-message batch that produced it is consumed in the same
professional commit transaction as the Evidence Response. Interaction
completion occurs afterward through a separate deterministic
`complete_interaction` command.

This prevents the same human input from being reprocessed after a
successful Evidence Response commit.

------------------------------------------------------------------------

# Deterministic Routing

Professional agents do not choose the next workflow step.

The **Router** evaluates explicit runtime state and deterministic
predicates.

Typical flow:

``` text
create job
    ↓
analysis
    ↓
┌───────────────────────────────┐
│ evidence sufficient?          │
└──────────────┬────────────────┘
               │
        yes    │    no
               │
               ▼
           evidence request
               ↓
           investigation
               ↓
        Evidence Response
               ↓
           re-analysis
               │
               ▼
             resume
               ↓
           evaluation
               ↓
┌───────────────────────────────┐
│ is_ready_to_submit == true?   │
└──────────────┬────────────────┘
               │
        yes    │    no
               │
               ▼
            complete
```

`ready_to_submit` is Evaluation state used by a routing predicate. It is
not a lifecycle phase.

------------------------------------------------------------------------

# Failure and Recovery

Crash recovery is a first-class architectural requirement.

The runtime distinguishes queue work from professional execution:

``` text
abandoned Event / Command
→ recovered through ownership and lease rules

interrupted professional provider call
→ recovered from persistent Execution state
```

Startup recovery reconciles:

-   Incomplete Executions.
-   Events and Commands left in processing states.
-   Expired ownership from prior runtime instances.
-   Incomplete professional commits.
-   Active or paused Interactions.
-   Discord provider messages not yet persisted locally.
-   Runtime Job projections.
-   Failure and Manual Review conditions.

The system prefers deterministic repair. When safe automatic recovery is
impossible, it records the failure and enters the defined manual-review
path rather than guessing.

------------------------------------------------------------------------

# V3 Architecture Models

The frozen V3 MVP runtime architecture is defined by eleven models under
`runtime/architecture/`:

``` text
artifact-execution-commit-model.md
discord-interaction-model.md
event-model.md
handler-interface-model.md
job-model.md
mvp-control-surface-model.md
mvp-runtime-deployment-model.md
operation-specification-registry-model.md
persistence-model.md
professional-invocation-model.md
routing-model.md
```

Together they define:

1.  Runtime Job state.
2.  Artifact and Execution commit semantics.
3.  Deterministic routing.
4.  Event and Command behavior.
5.  Handler responsibilities.
6.  Persistence and recovery.
7.  Discord human interaction.
8.  MVP control surfaces.
9.  Professional invocation.
10. Operation Specification Registry semantics.
11. Runtime composition and deployment.

The architecture completed its V3 conformance pass before implementation
planning began.

------------------------------------------------------------------------

# Repository Structure

The repository is organized around professional reasoning resources and
the V3 runtime architecture.

``` text
rapid-resume-system/
│
├── agents/
│   ├── researcher/
│   │   ├── contract.md
│   │   └── tasks/
│   ├── interviewer/
│   │   ├── contract.md
│   │   └── tasks/
│   ├── writer/
│   │   ├── contract.md
│   │   └── tasks/
│   ├── evaluator/
│   │   ├── contract.md
│   │   └── tasks/
│   └── supervisor/
│       └── contract.md
│
├── resources/
│   ├── architecture-principles.md
│   └── agent-contract-standard.md
│
├── schemas/
│   └── professional artifact schemas
│
├── runtime/
│   └── architecture/
│       ├── artifact-execution-commit-model.md
│       ├── discord-interaction-model.md
│       ├── event-model.md
│       ├── handler-interface-model.md
│       ├── job-model.md
│       ├── mvp-control-surface-model.md
│       ├── mvp-runtime-deployment-model.md
│       ├── operation-specification-registry-model.md
│       ├── persistence-model.md
│       ├── professional-invocation-model.md
│       └── routing-model.md
│
└── README.md
```

Implementation directories will be added during the implementation phase
rather than being prematurely specified in the architecture README.

------------------------------------------------------------------------

# Architecture vs. Implementation

RRS deliberately separates professional reasoning from runtime
implementation.

``` text
┌─────────────────────────────────────┐
│ Professional Architecture           │
│                                     │
│ contracts                           │
│ tasks                               │
│ schemas                             │
│ professional artifacts              │
│ professional authority              │
└──────────────────┬──────────────────┘
                   │
          Operation Specifications
                   │
┌──────────────────▼──────────────────┐
│ Runtime Architecture                │
│                                     │
│ jobs / commands / events            │
│ executions / interactions           │
│ persistence / recovery              │
│ routing / commits                   │
└──────────────────┬──────────────────┘
                   │
          implementation contracts
                   │
┌──────────────────▼──────────────────┐
│ Software Implementation             │
│                                     │
│ Python                              │
│ SQLite                              │
│ filesystem artifact store           │
│ Discord adapter                     │
│ container deployment                │
└─────────────────────────────────────┘
```

Implementation should implement the architecture.

It should not silently redefine it.

------------------------------------------------------------------------

# Design Principles

RRS follows several core principles.

### Separate professional responsibilities

Research, interviewing, writing, evaluation, and governance are
different professional functions.

### Separate cognition from orchestration

Professional agents reason about professional problems. Runtime
components manage state, routing, execution, persistence, and recovery.

### Give mutable state a clear authority

Professional evidence, resume presentation, evaluation, runtime
lifecycle, interaction state, and commit authority each have explicit
owners.

### Make artifacts partner-independent

Artifacts describe professional state rather than destinations or
workflow instructions.

### Keep agents unaware of runtime topology

Agents should not need to understand queues, retries, events, routing,
or transport.

### Use explicit artifacts instead of assumed shared memory

Every professional operation receives the authoritative context it
needs.

### Preserve factual provenance

Professional translation is encouraged. Historical fabrication is not.

### Separate evidence from presentation

The existence of evidence and the quality of its presentation are
different questions.

### Prefer deterministic orchestration

The runtime should derive routing and recovery from explicit state
rather than ask an AI agent what should happen next.

### Make professional operations convergent

Repeated execution with materially identical authoritative inputs should
converge on materially equivalent professional decisions.

### Treat failures as state

Interrupted work, stale output, unavailable evidence, and unsafe
recovery paths must be represented explicitly rather than hidden by
retries.

### Preserve auditability

Professional output should be traceable to its exact operation
specification, inputs, resources, Execution, and commit.

------------------------------------------------------------------------

# Current Development Status

## Completed

-   V2 professional agent architecture.
-   Agent contracts and task semantics.
-   Shared professional artifact schemas.
-   V3 runtime requirements analysis.
-   Runtime Job architecture.
-   Artifact and Execution commit architecture.
-   Deterministic routing architecture.
-   Event and Command architecture.
-   Handler interface and authority model.
-   Persistence and crash-recovery architecture.
-   Discord Interaction architecture.
-   MVP control-surface architecture.
-   Professional invocation architecture.
-   Operation Specification Registry architecture.
-   Single-container MVP deployment architecture.
-   Cross-model reconciliation and final conformance audit.

## Current Phase

**Implementation Planning**

The purpose of this phase is to translate the frozen architecture into
executable implementation contracts before production code is written.

Planned outputs include:

``` text
implementation inventory / traceability matrix
Python domain model
SQLite physical schema and migrations
transaction matrix
package and interface plan
Operation Specification definitions
implementation dependency graph
test architecture
GitHub implementation backlog
```

## Next Phase

**MVP Implementation**

Implementation will proceed incrementally, beginning with the
deterministic runtime kernel and a fake professional invoker before
connecting real professional agents and Discord.

The first target vertical slice is:

``` text
create_job
→ job_created
→ schedule_operation(generate_analysis)
→ Execution
→ fake professional invocation
→ staged JEA
→ professional commit
→ artifact_committed
→ evaluate_routing
→ Router
```

That slice will be tested under normal execution and simulated
crash/restart conditions before additional professional operations are
added.

------------------------------------------------------------------------

# MVP Scope

V3 V0.1 is intentionally narrow.

Included:

-   Existing Researcher, Interviewer, Writer, and Evaluator professional
    workflow.
-   Runtime Job orchestration.
-   Operation Specifications.
-   Commands, Events, and Executions.
-   SQLite control-plane persistence.
-   Filesystem professional artifact storage.
-   Deterministic routing.
-   Professional commit coordination.
-   Failure and recovery behavior.
-   Discord Evidence Request investigation.
-   Single-container deployment.

Deferred:

-   Analyst/Custodian professional-role split.
-   Information Request / Information Response runtime workflow.
-   Trello projection/integration.
-   Horizontal runtime scaling.
-   Multi-container shared SQLite operation.
-   PostgreSQL migration.
-   Additional external control surfaces not required for the MVP.

------------------------------------------------------------------------

# Governance

Changes to the following are architecture changes rather than casual
implementation edits:

-   Agent responsibilities.
-   Professional authority boundaries.
-   Contract semantics.
-   Task semantics.
-   Shared artifact semantics.
-   Schemas.
-   Runtime state ownership.
-   Operation Specification authority.
-   Commit semantics.
-   Routing semantics.
-   Persistence and recovery invariants.

The Supervisor may analyze and propose changes.

The human System Owner approves changes to the active architecture.

During implementation, a mismatch between code convenience and the
architecture should not be resolved by silently changing the
architecture in code. The mismatch should be surfaced explicitly and
either:

``` text
implementation changes to conform
```

or:

``` text
architecture change is proposed and reviewed
```

This preserves the architecture as an actual engineering contract.

------------------------------------------------------------------------

# Project Direction

RRS began as a manually coordinated set of specialized conversational
agents.

V3 turns that professional system into a recoverable software runtime
without sacrificing the separation of authority that made the agent
architecture useful.

The intended progression is:

``` text
V2
professional architecture
+ manual coordination

        ↓

V3 architecture
professional architecture
+ deterministic runtime model

        ↓

V3 implementation
professional architecture
+ executable runtime
+ durable state
+ crash recovery
+ human interaction
```

The immediate objective is no longer to design the runtime.

It is to **implement the runtime that has now been designed**.