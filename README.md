# Rapid Resume System

The **Rapid Resume System (RRS)** is a multi-agent system for producing targeted, evidence-based resumes from a reusable body of professional experience.

Instead of asking one AI conversation to research a job, remember an entire career, identify missing information, write a resume, and critique its own work, RRS separates those responsibilities among specialized AI agents.

The goal is to produce resumes that are:

* Highly targeted to a specific job.
* Grounded in confirmed professional evidence.
* Traceable to source experience.
* Written in recognizable civilian professional language.
* Independently evaluated before submission.
* Repeatable without reconstructing an entire career for every application.

> **Current status:** V2 architecture refactor.
>
> The current system operates through manually managed conversational AI agents. Automated orchestration, transport, and runtime infrastructure are outside the scope of this version.

---

# Why This Exists

Writing a strong targeted resume involves several different kinds of reasoning:

1. Understanding what an employer actually needs.
2. Searching a large career history for relevant evidence.
3. Determining how strongly that evidence supports each requirement.
4. Identifying factual gaps in the professional record.
5. Asking useful questions to recover undocumented experience.
6. Translating unusual, specialized, or military experience into recognizable civilian professional functions.
7. Selecting and presenting the strongest relevant evidence within limited resume space.
8. Evaluating the finished resume from the perspective of an ATS, recruiter, and hiring manager.

Trying to perform all of these functions inside one AI role creates competing objectives and unclear authority.

For example, a resume writer should present the candidate as strongly as the evidence allows. An evaluator should independently question whether the resulting resume actually demonstrates what the employer needs.

RRS separates these professional responsibilities.

---

# System Overview

The current system contains four production agents and one governance agent:

```text
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

Each agent receives the artifacts necessary to perform its task, exercises authority only within its own professional domain, and produces artifacts describing its resulting professional state.

Agents do not need to know:

* Which agent produced an input.
* Which agent will consume an output.
* How artifacts are transported.
* What happens before or after their task.
* What runtime workflow is being used.

This separation allows the reasoning architecture to remain independent of whatever software may eventually operate it.

---

# The Agents

## Researcher

The **Researcher** is the authoritative custodian of professional evidence and job-fit analysis.

Its responsibilities include:

* Analyzing target job descriptions.
* Searching the complete professional evidence set.
* Mapping job requirements to evidence.
* Distinguishing direct, transferable, partial, and unsupported experience.
* Maintaining authoritative professional evidence.
* Reconciling new evidence with existing evidence.
* Classifying supported civilian professional functions.
* Determining evidence sufficiency.
* Generating Job Experience Analyses.
* Generating Evidence Requests when material factual questions remain unresolved.

The Researcher owns analytical judgment about the professional evidence.

Other artifacts may identify deficiencies or provide new facts, but they do not independently redefine the authoritative evidence model.

---

## Interviewer

The **Interviewer** investigates factual questions with the human.

Given an Evidence Request, the Interviewer conducts a collaborative conversation designed to establish what actually happened.

Its responsibilities include:

* Asking targeted, adaptive questions.
* Helping the human recall relevant experiences.
* Clarifying responsibility.
* Clarifying ownership and decision authority.
* Establishing scope.
* Clarifying attribution.
* Identifying relevant systems, methods, and tools.
* Establishing results and outcomes.
* Preserving uncertainty and negative evidence.
* Producing an Evidence Response.

The Interviewer owns the quality of the human factual investigation.

It does **not** classify the resulting evidence, determine whether a job requirement is satisfied, or modify the authoritative professional evidence model.

---

## Writer

The **Writer** turns authorized professional evidence into a targeted resume.

The Writer owns presentation.

Its responsibilities include:

* Selecting authorized evidence for limited resume space.
* Translating evidence into concise resume language.
* Determining where evidence should appear.
* Presenting supported professional functions clearly.
* Translating unfamiliar experience into recognizable civilian terminology.
* Balancing technical depth, leadership, scope, and results.
* Aligning the resume with the target employer.
* Preserving factual provenance and attribution.
* Producing a Writer Content Manifest for traceability.

The Writer may reorganize supported experience for professional clarity.

It may not invent evidence, independently expand the authorized evidence set, or strengthen claims beyond what current analysis supports.

---

## Evaluator

The **Evaluator** independently judges the targeted resume as a hiring product.

It evaluates the resume from the perspectives of:

* Initial screening and ATS.
* Recruiter review.
* Hiring-manager review.

The central question is:

> **Does the visible resume actually demonstrate what this employer needs?**

The Evaluator assesses:

* Requirement coverage.
* Claim credibility.
* Recruiter comprehension.
* Professional positioning.
* Seniority and scope.
* ATS alignment.
* Screening risk.
* Factual integrity when supporting evidence is available.
* Submission readiness.

The Evaluator owns the judgment that a product deficiency exists.

It does not rewrite the resume, modify authoritative evidence, assign corrective ownership, or determine what happens next.

---

## Supervisor

The **Supervisor** governs the design of the system rather than producing resumes.

Its responsibilities include:

* Reviewing system architecture.
* Reviewing agent contracts.
* Reviewing task instructions.
* Reviewing schemas.
* Identifying authority conflicts.
* Identifying recurring process problems.
* Analyzing Process Feedback.
* Drafting proposed system improvements.
* Supporting controlled refactoring and continuous improvement.

The Supervisor may analyze and propose changes.

The human **System Owner** retains approval authority over changes to the active architecture.

---

# Separation of Authority

A central RRS principle is that important professional domains have explicit authority boundaries.

| Domain                                 | Authority    |
| -------------------------------------- | ------------ |
| Professional evidence and job analysis | Researcher   |
| Human factual investigation            | Interviewer  |
| Resume presentation                    | Writer       |
| Resume evaluation                      | Evaluator    |
| System architecture and governance     | Supervisor   |
| Approval of system changes             | System Owner |

This does **not** mean agents direct one another.

Instead, each artifact expresses professional state within the authority of the function that produced it.

For example:

```text
Resume Evaluation

"The resume does not sufficiently demonstrate vendor management."
```

That statement establishes a product condition.

A Job Experience Analysis may subsequently establish:

```text
"Existing evidence strongly supports vendor-performance management,
but that evidence is insufficiently visible in the current resume."
```

Or:

```text
"Current evidence does not establish direct vendor-performance
ownership. Additional factual investigation could materially
clarify the issue."
```

These statements are not competing judgments.

They answer different professional questions.

This separation prevents agents from second-guessing decisions outside their authority while preserving independent reasoning within their own domain.

---

# Current Task Model

Tasks represent **professional operations**, not workflow states.

```text
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

There is intentionally no separate:

```text
revise_resume
reevaluate_resume
recheck_analysis
integrate_evidence
```

When professional state changes, the appropriate operation simply runs again using the complete current artifact set.

This keeps task semantics stable as the system iterates.

---

# Idempotent Tasks

RRS tasks are designed to be **idempotent where practical**.

Running a task repeatedly with materially identical inputs should converge on materially equivalent professional decisions.

For example:

```text
Same target job
+ Same authorized evidence
+ Same product feedback
+ Same structural constraints

        ↓

generate_resume

        ↓

Materially same best resume
```

The Writer should not rewrite strong content merely because the task ran again.

The Evaluator should not invent new deficiencies merely because the resume was evaluated again.

The Researcher should not change evidence rankings without a material reason.

New information should produce justified change.

Unchanged information should produce convergence.

---

# Artifacts

RRS agents communicate professional state through explicit artifacts rather than assumed shared memory.

Core artifacts include:

* **Job Experience Records** — authoritative records of professional experience.
* **Job Experience Analysis** — analysis of professional evidence against a target job.
* **Evidence Request** — specification of a material factual question requiring human investigation.
* **Evidence Response** — factual information established through human investigation.
* **Targeted Resume** — the current application product.
* **Writer Content Manifest** — traceability between visible resume content and authorized evidence.
* **Resume Evaluation** — independent assessment of the current resume.
* **Process Feedback** — observations about recurring or material system-level friction.

Artifacts describe professional state.

They do not need to encode:

* Runtime routing.
* Destination agents.
* Workflow status.
* Corrective ownership.
* Transport mechanisms.
* Work queues.

This allows the same reasoning architecture to operate manually today and through different automation approaches later.

Governance work may additionally produce human-readable Governance Proposals, System Analyses, and Process Feedback Syntheses; these are governance documents rather than production-pipeline artifacts.

---

# How to Use the Current Version

V2 currently operates as a set of **bare conversational AI agents**.

There is no required orchestration software.

For each agent:

1. Start or maintain a dedicated AI conversation for that professional role.
2. Provide the agent's `contract.md`.
3. Provide the appropriate task instruction.
4. Supply the artifacts required by that task.
5. Allow the agent to perform its professional operation.
6. Save the resulting artifacts.
7. Manually provide relevant artifacts wherever they are needed next.

The human operator currently performs artifact coordination.

A simple resume-generation use case might involve:

```text
Target Job
+ Professional Evidence
        ↓
generate_analysis
        ↓
Job Experience Analysis
        ↓
generate_resume
        ↓
Targeted Resume
+ Writer Content Manifest
        ↓
evaluate_resume
        ↓
Resume Evaluation
```

If a material factual question needs human investigation, the relevant professional state may include:

```text
Material Factual Question
        ↓
request_evidence
        ↓
Evidence Request
        ↓
investigate_evidence_request
        ↓
Evidence Response
```

The resulting Evidence Response can then be supplied as current professional state when analysis is performed again.

These diagrams illustrate **human operation of the current system**.

They are not agent-internal workflow rules.

---

# Repository Structure

```text
rapid-resume-system/
│
├── agents/
│   │
│   ├── researcher/
│   │   ├── contract.md
│   │   └── tasks/
│   │       ├── generate-analysis.md
│   │       └── request-evidence.md
│   │
│   ├── interviewer/
│   │   ├── contract.md
│   │   └── tasks/
│   │       └── investigate-evidence-request.md
│   │
│   ├── writer/
│   │   ├── contract.md
│   │   └── tasks/
│   │       └── generate-resume.md
│   │
│   ├── evaluator/
│   │   ├── contract.md
│   │   └── tasks/
│   │       └── evaluate-resume.md
│   │
│   └── supervisor/
│       └── contract.md
│
├── resources/
│   ├── architecture-principles.md
│   └── agent-contract-standard.md
│
├── schemas/
│   └── [shared artifact schemas]
│
└── README.md
```

---

# Resource Types

## Architecture Principles

`resources/architecture-principles.md`

Defines the system-wide architectural rules.

It answers:

> **What principles govern the design of RRS?**

Agent contracts, task instructions, schemas, and future implementations should conform to these principles.

---

## Agent Contract Standard

`resources/agent-contract-standard.md`

Defines how agent contracts should be structured and what concerns belong in them.

It answers:

> **What must an RRS agent contract define?**

---

## Agent Contracts

`agents/<agent>/contract.md`

Contracts define durable professional identity, responsibility, and authority.

They answer:

> **Who is this agent, what does it own, and what authority does it have?**

Contracts should remain relatively stable across individual tasks.

---

## Task Instructions

`agents/<agent>/tasks/`

Task instructions define repeatable professional operations.

They answer:

> **What does this agent do when performing this particular kind of work?**

Tasks should describe professional transformations rather than workflow states.

---

## Schemas

`schemas/`

Schemas define the structure of shared artifacts.

They answer:

> **What information must this artifact contain?**

Schemas describe professional state.

They should not encode runtime topology.

---

# Architecture vs. Implementation

RRS separates **reasoning architecture** from **runtime implementation**.

Conceptually:

```text
Runtime / Human Operator
        │
        │ supplies context
        ▼
┌─────────────────────────────┐
│        Agent Reasoning      │
│                             │
│  Contract                   │
│  Task Instruction           │
│  Current Artifacts          │
│  Professional Judgment      │
└─────────────┬───────────────┘
              │
              │ produces
              ▼
       Professional Artifacts
```

The current repository primarily defines the **agent reasoning layer**.

How an artifact reaches an agent is an implementation concern.

The reasoning layer should therefore remain valid whether artifacts are transferred through:

* A human operator.
* Local software.
* An API.
* A message bus.
* A work queue.
* A future orchestration system.
* Another transport mechanism.

Runtime implementation should implement the professional architecture.

It should not redefine it.

---

# Design Philosophy

RRS follows several core principles.

### Separate professional responsibilities

Research, interviewing, writing, evaluation, and governance are different professional functions.

Keep them distinct.

### Give mutable professional state a clear authority

Especially professional evidence.

An artifact may observe another domain's state without assuming authority over it.

### Make artifacts partner-independent

Artifacts describe professional state rather than who should receive them or what should happen next.

### Keep agents unaware of runtime topology

Agents should understand their professional responsibilities and interfaces, not the mechanics of the system transporting their work.

### Use explicit artifacts instead of assumed shared memory

An agent should receive the professional context necessary to perform its operation.

### Preserve factual provenance

Professional translation is encouraged.

Historical fabrication is not.

### Recognize transferable experience without inflating it

Related capability should receive appropriate credit without being represented as identical experience.

### Separate evidence from presentation

A fact can exist without being well presented.

A resume can present something strongly without that presentation necessarily being well supported.

The architecture evaluates those questions separately.

### Prefer forward production over dependency seeking

An agent should produce the best professional artifact possible from the current state rather than attempt to control the surrounding process.

### Make tasks stable and repeatable

Different iterations should not require unnecessary task types.

### Optimize for convergence, not novelty

Repeated execution should change professional state when new information justifies change and remain stable when it does not.

### Keep implementation separate from cognition

The reasoning architecture should make sense without depending on any particular runtime technology.

---

# System Governance

Changes to:

* Agent responsibilities.
* Authority boundaries.
* Contracts.
* Task semantics.
* Shared artifact semantics.
* Schemas.

should be treated as architecture changes rather than casual prompt edits.

The Supervisor may analyze the system, identify recurring problems, and draft proposed improvements.

The human System Owner approves changes to the active architecture.

The governing architectural principles are documented in:

```text
resources/architecture-principles.md
```

That resource should be consulted when interpreting or modifying contracts, task instructions, schemas, or future runtime implementations.

---

# Current Development Status

The project is undergoing a **V2 architecture conformance refactor**.

The refactor aligns:

* Architecture principles.
* Agent contract standards.
* Individual agent contracts.
* Task instructions.
* Shared artifact schemas.

The current work focuses on stabilizing:

* Professional roles.
* Authority boundaries.
* Artifact interfaces.
* Partner independence.
* Evidence integrity.
* Idempotent task behavior.
* Continuous-improvement governance.

Runtime automation is intentionally outside the scope of this refactor.

The architecture should first be coherent when operated manually.

Automation can then implement those interfaces without changing the professional reasoning model.

---

# Project Goal

The long-term goal of the Rapid Resume System is not simply to generate resumes faster.

It is to create a reusable professional evidence system capable of answering:

> **Given everything this person has actually done, what is the strongest truthful case for their fit for this specific job?**

The targeted resume is one output of that system.

The more durable asset is the structured, reusable understanding of the person's professional experience.
