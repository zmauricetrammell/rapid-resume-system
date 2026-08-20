# Rapid Resume System

The **Rapid Resume System (RRS)** is a multi-agent workflow for producing targeted, evidence-based resumes and cover letters from a reusable body of professional experience.

Instead of asking one AI conversation to research a job, remember an entire career, write a resume, critique its own work, and collect missing information, RRS separates those responsibilities among specialized AI agents.

The goal is to produce resumes that are:

- Highly targeted to a specific job.
- Grounded in confirmed professional evidence.
- Traceable back to source experience.
- Written in recognizable civilian professional language.
- Independently evaluated before submission.
- Repeatable without requiring the user to reconstruct their career for every application.

> **Current status:** V2 architecture refactor.  
> The current implementation uses manually operated conversational AI agents. Automated agent communication, transport, and workflow infrastructure are intentionally outside the scope of this version.

---

## Why This Exists

Writing a strong targeted resume involves several different problems:

1. Understanding what the employer actually needs.
2. Searching a large career history for relevant evidence.
3. Determining whether that evidence directly or transferably satisfies the requirement.
4. Identifying missing evidence.
5. Asking useful questions to uncover experience that has not yet been documented.
6. Translating unusual or military experience into recognizable civilian professional functions.
7. Writing a concise resume from the strongest available evidence.
8. Evaluating the resulting resume from the perspective of an ATS, recruiter, and hiring manager.

Trying to perform all of these functions inside one AI role creates competing objectives.

For example, a resume writer is incentivized to make the candidate sound strong, while an evaluator should be skeptical about whether the resume actually proves its claims.

RRS separates these concerns.

---

# System Overview

The current system contains four execution agents and one governance agent.

```text
                     ┌──────────────────────┐
                     │      Researcher      │
                     │                      │
                     │ Evidence Custodian   │
                     │ Job Analysis         │
                     └──────────┬───────────┘
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
                 ▼                             ▼
        ┌────────────────┐            ┌────────────────┐
        │     Writer     │            │  Interviewer   │
        │                │            │                │
        │ Resume & Cover │            │ Human Evidence │
        │ Letter Writing │            │ Acquisition    │
        └───────┬────────┘            └───────┬────────┘
                │                             │
                ▼                             │
        ┌────────────────┐                    │
        │   Evaluator    │                    │
        │                │                    │
        │ Independent    │                    │
        │ Product Review │                    │
        └───────┬────────┘                    │
                │                             │
                └──────────────┬──────────────┘
                               │
                               ▼
                         Researcher
```

The **Supervisor** exists outside the production workflow and governs the design of the system itself.

---

# The Agents

## Researcher

The **Researcher** is the authoritative custodian of professional evidence.

Its job is to understand the target position and determine which confirmed career evidence best supports the application.

The Researcher:

- Analyzes job descriptions.
- Searches professional experience.
- Maps requirements to evidence.
- Distinguishes direct from transferable experience.
- Maintains Job Experience Records.
- Reconciles new evidence with existing evidence.
- Identifies evidence gaps.
- Generates Job Experience Analyses.
- Generates Evidence Requests when more information is required.

The Researcher owns the evidence model.

Other agents may consume evidence or identify deficiencies, but they do not independently change the authoritative career evidence.

---

## Interviewer

The **Interviewer** acquires professional evidence from the human user.

When the Researcher identifies something important that cannot be established from existing evidence, it creates an Evidence Request.

The Interviewer uses that request to conduct a collaborative interview.

The Interviewer:

- Asks targeted questions.
- Helps the user recall relevant experiences.
- Clarifies responsibility and ownership.
- Establishes scope.
- Clarifies attribution.
- Identifies results and outcomes.
- Confirms facts.
- Produces an Evidence Response.

The Interviewer does **not** decide how new information should modify the career evidence model.

That responsibility belongs to the Researcher.

---

## Writer

The **Writer** turns Researcher-authorized evidence into application materials.

The Writer owns presentation.

It decides:

- Which authorized evidence deserves limited resume space.
- How evidence should be phrased.
- Where evidence should appear.
- How professional functions should be presented.
- How to translate experience into recognizable civilian terminology.
- How to balance technical depth, leadership, scope, and results.
- How to target the document to the employer.

The Writer produces:

- Targeted resumes.
- Targeted cover letters.
- Supporting content manifests for traceability.

The Writer may reorganize supported experience for professional clarity, but it may not invent evidence or expand beyond the Researcher's authorized evidence boundary.

---

## Evaluator

The **Evaluator** independently judges the resulting resume as a hiring product.

It evaluates the resume from the perspectives of:

- Initial screening and ATS.
- Recruiter review.
- Hiring-manager review.

The Evaluator asks:

> Does the resume actually demonstrate what this employer needs?

It assesses:

- Requirement coverage.
- Evidence strength.
- Claim credibility.
- Recruiter comprehension.
- Professional positioning.
- Screening risk.
- Submission blockers.
- Overall readiness.

The Evaluator owns the judgment that a visible product deficiency exists.

It does not own the upstream solution.

If evidence appears insufficient, the Researcher determines what evidence can resolve the problem. If the evidence is sufficient but poorly communicated, the Writer determines how to improve the presentation.

---

## Supervisor

The **Supervisor** governs the system rather than producing resumes.

It exists to support controlled continuous improvement.

The Supervisor:

- Reviews architecture.
- Reviews agent contracts.
- Reviews task instructions.
- Reviews schemas.
- Identifies role conflicts.
- Analyzes recurring process problems.
- Drafts proposed improvements.
- Supports system refactoring.

The Supervisor may propose changes, but the human **System Owner retains approval authority** over changes to the active system.

---

# Separation of Responsibilities

A central design principle of RRS is that each important domain has one authoritative owner.

| Domain | Authoritative Agent |
|---|---|
| Professional evidence | Researcher |
| Human evidence acquisition | Interviewer |
| Resume and cover-letter presentation | Writer |
| Resume screening judgment | Evaluator |
| System architecture and governance | Supervisor |
| Approval of system changes | System Owner |

This prevents agents from arguing over the same decision.

For example:

```text
Evaluator:

"The resume does not sufficiently demonstrate vendor management."

                    ↓

Researcher:

"What evidence do we have that can establish vendor management?"

                    ↓

Writer:

"How should that authorized evidence be presented clearly?"

                    ↓

Evaluator:

"Does the revised resume now demonstrate it?"
```

Each agent accepts the judgments belonging to another agent's domain while retaining authority over the solution within its own domain.

---

# Evidence Acquisition

New human evidence passes through the Researcher.

```text
Writer or Evaluator identifies deficiency
                │
                ▼
           Researcher
                │
        Search existing evidence
                │
          ┌─────┴─────┐
          │           │
          ▼           ▼
     Evidence      Evidence
      exists      insufficient
          │           │
          │           ▼
          │     Evidence Request
          │           │
          │           ▼
          │      Interviewer
          │           │
          │           ▼
          │     Human Interview
          │           │
          │           ▼
          │    Evidence Response
          │           │
          └─────┬─────┘
                ▼
           Researcher
                │
                ▼
      Authoritative Evidence
```

This prevents unnecessary interviews and ensures that one agent remains responsible for reconciling the career evidence.

---

# Current V2 Task Model

Tasks represent **kinds of work**, not workflow states.

```text
Researcher
├── generate_analysis
└── request_evidence

Interviewer
└── investigate_evidence_request

Writer
├── generate_resume
└── generate_cover_letter

Evaluator
└── evaluate_resume
```

There is intentionally no separate:

```text
revise_resume
reevaluate_resume
recheck_analysis
```

If new information becomes available, the appropriate task simply runs again using the complete current artifact set.

---

# Idempotent Tasks

RRS tasks are designed to be idempotent where practical.

That means running a task repeatedly with materially identical inputs should produce materially stable decisions.

For example:

```text
Same job
+ Same evidence
+ Same feedback
+ Same constraints

        ↓

generate_resume

        ↓

Materially same best resume
```

The Writer should not rewrite strong content merely because the task ran again.

Likewise, the Evaluator should not invent new criticisms merely because a resume is being evaluated again.

New information should produce change.

Unchanged information should generally produce convergence.

---

# Artifacts

Agents exchange information through explicit artifacts rather than relying on shared conversational memory.

Important artifacts include:

- Job Experience Records.
- Job Experience Analysis.
- Evidence Requests.
- Evidence Responses.
- Targeted Resumes.
- Targeted Cover Letters.
- Writer Content Manifests.
- Resume Evaluations.
- Process Feedback.

This makes the system easier to inspect, reproduce, audit, and eventually automate.

In the current version, the human operator manually transfers these artifacts between agents.

---

# How to Use the Current Version

V2 currently operates as a set of **bare conversational AI agents**.

There is no required orchestration software.

For each agent:

1. Start or maintain a dedicated AI conversation for that role.
2. Provide the agent's `contract.md`.
3. Provide the appropriate task instruction.
4. Supply the artifacts required by that task.
5. Allow the agent to perform its work.
6. Save its output.
7. Provide that output to the next appropriate agent.

For example:

```text
Target Job
    │
    ▼
Researcher
    │
    ▼
Job Experience Analysis
    │
    ▼
Writer
    │
    ▼
Targeted Resume
    │
    ▼
Evaluator
```

If the Evaluator identifies insufficient evidence:

```text
Evaluator finding
       │
       ▼
Researcher
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
Researcher
       │
       ▼
Updated analysis
       │
       ▼
Writer
```

The human user currently performs these transfers manually.

---

# Repository Structure

The repository is organized around the system's agents and shared resources.

```text
rapid-resume-system/
│
├── agents/
│   │
│   ├── researcher/
│   │   ├── contract.md
│   │   └── tasks/
│   │
│   ├── interviewer/
│   │   ├── contract.md
│   │   └── tasks/
│   │
│   ├── writer/
│   │   ├── contract.md
│   │   └── tasks/
│   │
│   ├── evaluator/
│   │   ├── contract.md
│   │   └── tasks/
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

### Contracts

Contracts define durable agent behavior:

> Who is this agent, what does it own, and what authority does it have?

### Task Instructions

Task instructions define repeatable operations:

> What does this agent do when performing this particular kind of work?

### Schemas

Schemas define structured artifacts:

> What information must this artifact contain?

### Resources

Resources contain system-wide standards and shared guidance.

---

# Architecture vs. Implementation

RRS intentionally separates the reasoning architecture from the software that may eventually operate it.

Conceptually:

```text
┌───────────────────────────────────────────────┐
│ Future Python Handler                         │
│                                               │
│ Agent lifecycle                               │
│ Prompt loading                                │
│ Artifact assembly                             │
│ Model invocation                              │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│ Agent Reasoning                               │
│                                               │
│ Contract                                      │
│ Task Instruction                              │
│ Current Artifacts                             │
│ Professional Judgment                         │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│ Future Connectors                             │
│                                               │
│ Messaging                                     │
│ Storage                                       │
│ GitHub                                        │
│ Discord                                       │
│ Trello                                        │
│ Other APIs                                    │
└───────────────────────────────────────────────┘
```

The **current repository focuses on the agent reasoning layer**.

Future software should implement these boundaries rather than redefine them.

---

# What Is Not Implemented Yet

The current V2 architecture does not implement automated multi-agent communication.

Planned or possible future capabilities include:

- Python agent handlers.
- Persistent agent instances.
- Automated artifact transport.
- Message buses.
- Discord integration.
- Trello integration.
- Automated work queues.
- API-based model invocation.
- Automated artifact persistence.
- Automated notifications.
- Human-in-the-loop workflow interfaces.

These are intentionally outside the current V2 refactor.

The current priority is to establish stable agent behavior and interfaces before automating them.

---

# Design Philosophy

RRS follows several core principles:

**Separate reasoning responsibilities.**  
Research, interviewing, writing, evaluation, and governance are different professional functions and should remain distinct.

**Keep one authoritative owner for mutable information.**  
Especially for professional evidence.

**Use explicit artifacts instead of assumed shared memory.**  
An agent should receive what it needs to perform its task.

**Preserve factual provenance.**  
Professional translation is encouraged. Historical fabrication is not.

**Recognize transferable experience without inflating it.**  
Related experience should receive appropriate credit without being misrepresented as identical experience.

**Make tasks stable and repeatable.**  
Different workflow iterations should not create unnecessary task types.

**Optimize for convergence, not novelty.**  
Repeated execution should improve the product when new information exists and remain stable when it does not.

**Keep implementation separate from cognition.**  
Agents should understand their professional responsibilities, not the mechanics of the software transporting their work.

**Automate only after the conceptual interface is stable.**  
The architecture should make sense without Trello, Discord, Python, or any other transport technology.

---

# Current Development Status

The project is currently undergoing a **V2 architecture conformance refactor**.

The purpose of this refactor is to align:

- Architecture principles.
- Agent contract standards.
- Individual agent contracts.
- Task instructions.
- Shared schemas.

The refactor specifically removes assumptions about future workflow infrastructure while preserving the established:

- Agent roles.
- Authority boundaries.
- Evidence model.
- Professional personas.
- Idempotent task behavior.
- Continuous-improvement model.

After the conceptual architecture is stable, later iterations can introduce automation without coupling agent reasoning to any particular transport system.

---

# System Governance

Changes to agent responsibilities, authority boundaries, contracts, task semantics, or schemas should be treated as architecture changes rather than casual prompt edits.

The Supervisor may analyze the system and propose improvements.

The System Owner approves changes to the active architecture.

The governing architecture for the current version is documented in:

```text
resources/architecture-principles.md
```

That document should be consulted when interpreting or modifying agent contracts, task instructions, or schemas.

---

# Project Goal

The long-term goal of the Rapid Resume System is not simply to generate resumes faster.

It is to create a reusable professional evidence system capable of answering:

> Given everything this person has actually done, what is the strongest truthful case for their fit for this specific job?

The resume is one output of that system.

The underlying asset is the structured, reusable understanding of the person's professional experience.