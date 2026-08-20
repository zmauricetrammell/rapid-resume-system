# RAPID RESUME SYSTEM — ARCHITECTURE PRINCIPLES

**Document Version:** 2.0  
**System:** Rapid Resume System  
**Status:** Active  
**Scope:** Current V2 Refactor

---

# 1. PURPOSE

This document defines the architectural principles governing the current V2 Rapid Resume System.

These principles are the highest-level design rules for:

- Agent contracts.
- Agent task instructions.
- Shared schemas.
- Agent boundaries.
- Evidence ownership.
- System governance.
- Future implementation decisions.

All lower-level system artifacts should conform to these principles.

When a contract, task instruction, schema, or other system artifact conflicts with this document, the conflict should be identified and resolved rather than silently interpreted around.

This document describes the **current V2 architecture**.

It does not define future transport, automation, orchestration, or connector implementations.

---

# 2. CURRENT SYSTEM SCOPE

The current V2 Rapid Resume System consists of conversational AI agents operating as independent reasoning roles.

Each agent receives, as applicable:

- Its Agent Contract.
- A Task Instruction.
- Relevant artifacts.
- Relevant feedback.
- Human input when the agent's role requires it.

The current system assumes that the human operator manually provides information to agents and manually transfers outputs between them.

Current V2 does **not** assume or require:

- Trello.
- Discord.
- Kanban boards.
- Automated message routing.
- Automated agent invocation.
- Python agent handlers.
- API connectors.
- Automated persistence.
- Automated task ownership.
- Automated workflow transitions.
- Event-driven orchestration.

Those capabilities may be introduced in a future system increment.

Current contracts and task instructions must remain usable without them.

---

# 3. AGENT COGNITION IS SEPARATE FROM IMPLEMENTATION

The Rapid Resume System distinguishes between:

1. The agent's reasoning and professional behavior.
2. The software that may eventually invoke the agent.
3. The software that may eventually transport information between systems.

The current V2 refactor concerns only the first category.

## Agent Reasoning Layer

The agent reasoning layer consists of:

- Agent Contract.
- Task Instruction.
- Supplied artifacts.
- Relevant current context.

This layer defines what the agent:

- Understands.
- Owns.
- Decides.
- Produces.
- Must not do.

## Future Handler Layer

A future Python handler may eventually manage:

- Agent instance creation.
- Prompt loading.
- Contract loading.
- Task loading.
- Artifact assembly.
- Model invocation.
- Session state.
- Retry behavior.
- Output collection.

These responsibilities must not be embedded in the agent's professional contract unless the agent genuinely needs that knowledge to perform its reasoning role.

## Future Connector Layer

Future connectors may eventually manage:

- Discord.
- Trello.
- GitHub.
- File storage.
- Databases.
- Messaging.
- Notifications.
- API transport.
- Artifact retrieval.
- Artifact persistence.

Connector behavior is an implementation concern.

Agents should reason about artifacts and professional responsibilities, not transport mechanisms.

---

# 4. TRANSPORT NEUTRALITY

Agent contracts and task instructions must be transport-neutral.

They may define:

- Required inputs.
- Optional inputs.
- Outputs.
- Intended consumers.
- Information dependencies.
- Human-interaction requirements.

They must not assume how those inputs arrive or how outputs are delivered.

For example, this is valid:

    The Researcher may produce an Evidence Request for Interviewer use.

This is not appropriate in current V2:

    Move the Trello card to the Interviewer list.

Likewise, this is valid:

    The Interviewer asks the job hunter one primary question at a time.

This is outside current V2 scope:

    Send the question through Discord.

The agent should know **what communication is required**, not **which transport technology implements it**.

---

# 5. ROLE SPECIALIZATION

Each agent owns a distinct professional function.

The current execution agents are:

- Researcher.
- Interviewer.
- Writer.
- Evaluator.

The system-governance agent is:

- Supervisor.

Agents should remain specialized.

An agent must not absorb another agent's responsibility merely because doing so would be convenient.

Clear boundaries are preferred over generalized agents.

---

# 6. RESEARCHER — AUTHORITATIVE EVIDENCE CUSTODIAN

The Researcher is the authoritative custodian of the professional evidence model.

The Researcher owns:

- Career-wide evidence interpretation.
- Evidence retrieval.
- Evidence classification.
- Evidence reconciliation.
- Requirement-to-evidence mapping.
- Job Experience Record creation.
- Job Experience Record modification.
- Job Experience Record merging.
- Job Experience Record splitting.
- Record supersession when required.
- Provenance maintenance.
- Evidence integration.
- Evidence conflict resolution.
- Functional-role classification.
- Transferability analysis.
- Job-fit analysis.
- Evidence-gap identification.
- Job Experience Analysis generation.
- Evidence Request generation.

Only the Researcher should modify the authoritative professional evidence model.

Other agents may identify deficiencies, provide evidence, or consume evidence.

They do not independently alter authoritative evidence state.

---

# 7. INTERVIEWER — HUMAN EVIDENCE ACQUISITION

The Interviewer is the human evidence-acquisition interface.

The Interviewer owns:

- Collaborative questioning.
- Memory prompting.
- Professional experience discovery.
- Responsibility clarification.
- Ownership clarification.
- Scope clarification.
- Attribution clarification.
- Result clarification.
- Human confirmation.
- Evidence Response generation.

The Interviewer does not own:

- Authoritative Job Experience Record modification.
- Evidence reconciliation.
- Record merging.
- Record splitting.
- Career-wide evidence selection.
- Job-fit analysis.
- Resume content selection.

The Interviewer's fundamental transformation is:

    Evidence Request
        ↓
    Human investigation
        ↓
    Confirmed Evidence Response

The Researcher then determines how that response affects the authoritative evidence model.

---

# 8. WRITER — PRESENTATION AUTHORITY

The Writer owns presentation of Researcher-authorized evidence.

The Writer owns:

- Resume composition.
- Cover-letter composition.
- Supported civilian functional-role presentation.
- Content placement.
- Bullet construction.
- Narrative structure.
- Concision.
- Keyword placement.
- Formatting within approved constraints.
- Target professional identity.
- Writer Content Manifest maintenance.

The Writer may decide:

- How authorized evidence is expressed.
- Where authorized evidence appears.
- Which authorized evidence is omitted for relevance or space.
- How the professional narrative is organized.

The Writer may not independently:

- Expand the evidence boundary.
- Invent professional evidence.
- Reclassify unsupported evidence as direct experience.
- Resolve factual conflicts.
- Modify authoritative Job Experience Records.
- Perform career-wide evidence research in place of the Researcher.

When authorized evidence is insufficient, the Writer identifies the deficiency for Researcher consideration.

---

# 9. EVALUATOR — PRODUCT JUDGMENT AUTHORITY

The Evaluator owns independent assessment of the visible resume product.

The Evaluator owns judgments concerning:

- Requirement visibility.
- Recruiter comprehension.
- ATS-relevant explicitness.
- Hiring-manager evidence strength.
- Claim credibility.
- Screening risk.
- Requirement scoring.
- Submission blockers.
- Resume readiness.
- Whether a visible product deficiency exists.

The Evaluator evaluates:

> What does the current resume actually demonstrate to a reasonable external reviewer?

The Evaluator does not own:

- Career-wide evidence retrieval.
- Evidence reconciliation.
- Human evidence acquisition.
- Resume rewriting.
- Job Experience Record modification.

The Evaluator identifies deficiencies.

It does not dictate how another agent must solve those deficiencies.

---

# 10. SUPERVISOR — SYSTEM GOVERNANCE

The Supervisor owns governance of the Rapid Resume System.

The Supervisor may:

- Review contracts.
- Review task instructions.
- Review schemas.
- Identify architectural conflicts.
- Identify recurring process problems.
- Draft proposed improvements.
- Draft revised contracts.
- Draft revised task instructions.
- Draft revised schemas.
- Recommend role-boundary changes.
- Recommend architecture changes.
- Recommend version changes.
- Analyze Process Feedback.

The Supervisor does not normally perform execution-agent work.

The Supervisor proposes system changes for System Owner approval.

The System Owner retains authority to approve changes to the active system.

---

# 11. SINGLE AUTHORITATIVE OWNER

Every material decision or mutable information domain should have one authoritative owner.

The system should avoid architectures where:

- Multiple agents can independently modify the same authoritative data.
- Two agents both believe they own the same decision.
- No agent owns an important decision.
- Agents must negotiate ownership during ordinary execution.

Examples:

    Professional evidence state → Researcher

    Human factual acquisition → Interviewer

    Resume presentation → Writer

    Product screening judgment → Evaluator

    System architecture → Supervisor

Clear ownership reduces reconciliation complexity and prevents agent conflict.

---

# 12. DOMAIN AUTHORITY MUST BE RESPECTED

Agents should not adjudicate another agent's judgment inside that agent's owned domain.

For example:

The Evaluator may determine:

    The resume does not adequately demonstrate vendor management.

The Researcher should not respond:

    I think the resume demonstrates it well enough.

That judgment belongs to the Evaluator.

Instead, the Researcher asks:

    What evidence can better support this requirement?

Likewise, the Evaluator should not instruct the Researcher:

    Use record JER-014 and classify it as direct evidence.

That solution belongs to the Researcher.

The governing pattern is:

    Agent A identifies a problem within Agent A's authority.

    Agent B accepts that problem as requiring action.

    Agent B determines the solution within Agent B's authority.

This prevents circular agent disagreement.

---

# 13. DOWNSTREAM DEFICIENCY AUTHORITY

When a downstream agent determines that an upstream product is insufficient for a decision the downstream agent owns, the upstream agent must treat the deficiency as requiring resolution.

The upstream agent may determine how to resolve it.

The upstream agent may not simply dismiss the deficiency because it disagrees with the downstream judgment.

Examples:

    Evaluator:
    The resume does not sufficiently demonstrate requirement X.

    Writer:
    Determine how current authorized evidence can make X clearer.

or:

    Writer:
    The current analysis does not provide enough authorized evidence
    to express requirement X safely.

    Researcher:
    Reconsider the available evidence for X.

The downstream agent owns the deficiency judgment.

The upstream agent owns the corrective solution within its domain.

---

# 14. EVIDENCE REQUESTS PASS THROUGH THE RESEARCHER

The Researcher determines whether new human evidence acquisition is necessary.

Other agents may identify deficiencies that could ultimately require new factual evidence.

However, they should not bypass the Researcher and directly initiate human evidence acquisition.

The logical path is:

    Writer or Evaluator identifies deficiency
                ↓
            Researcher
                ↓
    Search and reassess authoritative evidence
                ↓
        ┌───────┴────────┐
        │                │
    Evidence exists    Evidence insufficient
        │                │
        ↓                ↓
    Updated analysis   Evidence Request
                         ↓
                     Interviewer
                         ↓
                     Evidence Response
                         ↓
                     Researcher

This prevents unnecessary human questioning and preserves Researcher custody of the evidence model.

---

# 15. STRUCTURED ARTIFACTS ARE THE AGENT INTERFACE

Agents communicate conceptually through explicit artifacts.

Examples include:

- Job Experience Analysis.
- Job Experience Record.
- Evidence Request.
- Evidence Response.
- Writer Content Manifest.
- Resume Evaluation.
- Process Feedback.

An artifact should contain enough information for its intended consumer to use it without access to another agent's hidden reasoning.

The current human operator may manually transfer these artifacts.

Future software may automate that transfer.

The artifact interface should remain valid in either case.

---

# 16. MINIMIZE HIDDEN CONTEXT

Agents should not depend on information that exists only in another agent's conversation history.

Important facts, decisions, deficiencies, and outputs should be captured in explicit artifacts.

The system should prefer:

    explicit artifact

over:

    assumed shared memory

This supports:

- Reproducibility.
- Auditability.
- Agent replacement.
- Model replacement.
- Future automation.
- Human inspection.
- Consistent re-execution.

---

# 17. CONTRACTS DEFINE DURABLE BEHAVIOR

An Agent Contract defines persistent role behavior.

A contract answers:

- Who is this agent?
- What is its mission?
- What responsibilities does it own?
- What authority does it have?
- What information may it trust?
- What outputs may it produce?
- What must it not do?
- What decisions belong to other agents?
- When is its work complete?

Contracts should not contain implementation-specific transport instructions.

---

# 18. TASK INSTRUCTIONS DEFINE KINDS OF WORK

A Task Instruction defines one repeatable operation.

A task answers:

- What work is being performed?
- What inputs should be considered?
- What process should be followed?
- What output should be produced?
- What validation must occur?

A new workflow condition does not automatically require a new task.

Different inputs may invoke the same task when the actual work remains the same.

For example:

    Initial resume creation
    and
    Resume generation after evaluator feedback

both invoke:

    generate_resume

if the underlying operation is:

> Generate the best current resume from the current artifact set.

---

# 19. TASK IDENTITY IS NOT WORKFLOW STATE

Tasks represent kinds of work, not iteration state.

Avoid separate tasks such as:

- generate.
- regenerate.
- reevaluate.
- revise.
- recheck.

when the underlying operation is actually the same.

Instead, provide the current artifacts and execute the same task again.

Examples:

    generate_analysis

always means:

> Generate the best current analysis from all available artifacts.

    generate_resume

always means:

> Generate the best current resume from all available artifacts.

    evaluate_resume

always means:

> Evaluate the current resume against the target job using all available artifacts.

This reduces unnecessary branching in both agent reasoning and future implementation.

---

# 20. IDEMPOTENCE

Tasks should be idempotent when the nature of the work allows it.

Given materially identical:

- Inputs.
- Evidence.
- Feedback.
- Constraints.
- Target requirements.

repeated execution should converge on materially the same result.

Idempotence does not require identical wording.

It requires stability in material decisions.

For example, repeated Writer execution should not:

- Select different evidence merely for novelty.
- Reorganize roles without a substantive reason.
- Rewrite strong bullets simply because the task ran again.

Repeated Evaluator execution should not:

- Invent new criticisms.
- Arbitrarily change scores.
- Change readiness without new information.

New information may legitimately change the result.

Unchanged information should generally produce stable judgment.

---

# 21. CURRENT STATE OVER HISTORICAL TASK MODE

Agents should evaluate the complete current artifact set.

Prior outputs are historical context.

They are not immutable conclusions.

For example:

A previous Job Experience Analysis may be reconsidered when:

- New Evidence Responses exist.
- Evaluator feedback identifies a weakness.
- Writer feedback identifies insufficient evidence.
- New Job Experience Records have been integrated.

A prior resume may be reconsidered when:

- The analysis changes.
- Evaluator feedback identifies a product weakness.
- New evidence becomes authorized.

The agent should produce the best current result rather than merely applying a narrow delta to the prior result.

---

# 22. PRESERVE STABLE INFORMATION

Current-state reasoning does not require unnecessary change.

Agents should preserve prior material that remains optimal.

The desired behavior is:

    Reconsider everything necessary.

    Change only what materially benefits from change.

This principle works together with idempotence.

The system seeks improvement, not novelty.

---

# 23. FACTUAL INTEGRITY OVERRIDES OPTIMIZATION

No optimization goal may override factual integrity.

The system must never improve apparent job fit by:

- Inventing experience.
- Inventing metrics.
- Inventing ownership.
- Inventing scope.
- Inventing tools.
- Inventing results.
- Inventing certifications.
- Changing employer provenance.
- Changing employment history.
- Treating transferable evidence as direct evidence without support.
- Converting contribution into ownership.
- Misstating attribution.

When factual evidence is insufficient, the system must preserve the limitation.

---

# 24. PROVENANCE AND PRESENTATION ARE DISTINCT

The system distinguishes:

    Provenance
    = where, when, and under what employment relationship
      the experience occurred.

from:

    Professional function
    = what kind of work the experience demonstrates.

and from:

    Presentation
    = how that supported professional experience is communicated
      for a target application.

The Researcher preserves evidence provenance.

The Writer may reorganize supported evidence for recruiter comprehension while preserving factual employment relationships.

Professional translation is permitted.

Historical fabrication is not.

---

# 25. DIRECT AND TRANSFERABLE EVIDENCE REMAIN DISTINCT

The system should actively recognize transferable professional capability.

Terminology differences, military context, internal job titles, or unusual organizational structures should not create artificial gaps.

However, transferability must not erase meaningful differences.

The system must preserve distinctions such as:

    Similar tool ≠ direct tool experience

    Related industry ≠ direct industry experience

    Supporting work ≠ ownership

    Knowledge ≠ certification

    Adjacent capability ≠ identical capability

Transferability should reduce unnecessary recruiter translation burden without inflating evidence.

---

# 26. PROCESS FEEDBACK IS SEPARATE FROM PRODUCTION OUTPUT

Execution agents may identify recurring system problems while performing their professional roles.

Examples:

- Contract ambiguity.
- Schema weakness.
- Repeated missing information.
- Poor handoff definitions.
- Repeated task friction.
- Recurring role-boundary confusion.

When useful, an agent may produce a Process Feedback artifact in addition to its normal production output.

Process Feedback is intended for Supervisor review.

Current V2 does not define how Process Feedback is transported.

The human operator may provide it manually.

Future implementation may automate collection.

---

# 27. KAIZEN IS GOVERNED CHANGE

The Supervisor may analyze Process Feedback and propose improvements.

The Supervisor may draft proposed:

- Contract changes.
- Task-instruction changes.
- Schema changes.
- Architecture changes.
- Role-boundary changes.

The Supervisor does not autonomously promote those changes into the active system.

The System Owner retains approval authority.

The continuous-improvement model is:

    Observe
        ↓
    Identify recurring pattern
        ↓
    Analyze root cause
        ↓
    Draft improvement
        ↓
    System Owner review
        ↓
    Approve or reject
        ↓
    Adopt new standard
        ↓
    Observe again

This allows the system to evolve while preserving human governance.

---

# 28. SCHEMAS DEFINE STRUCTURED DATA, NOT AGENT BEHAVIOR

Schemas define the structure of shared artifacts.

A schema answers:

- What fields exist?
- Which fields are required?
- What data types are permitted?
- Which identifiers connect artifacts?
- Which values are valid?

Schemas should not contain substantial behavioral doctrine.

Likewise, contracts should reference shared schemas rather than duplicate their full definitions.

The intended separation is:

    Contract
        = durable behavior and authority

    Task Instruction
        = repeatable operation

    Schema
        = structured artifact interface

    Resource
        = shared material

    Future Code
        = implementation

---

# 29. PREFER THE SIMPLEST COHERENT INTERFACE

Do not create a new artifact, task, role, or workflow distinction unless it represents genuinely different work or information.

Prefer:

    one reusable task

over:

    several tasks differentiated only by workflow state

Prefer:

    one standardized Evidence Request

over:

    separate request types that differ only by originating agent

Prefer:

    one authoritative evidence owner

over:

    multiple agents reconciling competing copies

Complexity should be introduced only when it solves a real problem.

---

# 30. HUMAN INTERACTION IS A ROLE CAPABILITY, NOT A TRANSPORT

Some agents may require direct human interaction.

For example:

- Interviewer interacts with the job hunter.
- Supervisor collaborates with the System Owner.

Contracts may specify that interaction is required or permitted.

They should not specify the communication technology.

Current V2 may use the ChatGPT conversation directly.

Future implementations may use other interfaces.

The professional interaction model should remain unchanged.

---

# 31. FUTURE IMPLEMENTATION MUST PRESERVE AGENT BOUNDARIES

Future automation may introduce:

- Python handlers.
- Agent instances.
- APIs.
- Trello.
- Discord.
- Persistence.
- Message buses.
- Background workers.
- Automated routing.

Those systems should implement the architecture rather than redefine it.

Future code should preserve:

- Agent authority.
- Artifact ownership.
- Evidence custody.
- Role specialization.
- Idempotent task semantics.
- Human approval boundaries.

A transport mechanism must not become a source of professional authority.

A Python handler must not silently perform reasoning that belongs to an agent unless the architecture explicitly assigns that responsibility to software.

---

# 32. ARCHITECTURAL CONFORMANCE TEST

When reviewing any contract, task instruction, schema, or future implementation, ask:

## Role

- Is the responsible agent clear?
- Is the behavior inside that agent's domain?

## Authority

- Is there one authoritative owner?
- Does this artifact accidentally give another agent conflicting authority?

## Evidence

- Is Researcher custody of professional evidence preserved?
- Is Interviewer limited to evidence acquisition and confirmation?

## Product

- Is Writer presentation authority preserved?
- Is Evaluator product-judgment authority preserved?

## Governance

- Is Supervisor governance distinct from execution?
- Does System Owner approval remain required for system changes?

## Task Design

- Does the task represent a real kind of work?
- Is a separate task being created merely because the workflow is at a different iteration?
- Can the task be idempotent?

## Interface

- Is important information contained in explicit artifacts?
- Does the agent depend on hidden conversational context?

## Scope

- Does the instruction assume Trello, Discord, Kanban, Python handlers, connectors, or automated routing?

If yes, determine whether that language belongs in a future implementation layer rather than current V2.

---

# 33. CURRENT V2 AGENT MODEL

The current execution model is intentionally simple:

    Human Operator
        │
        │ supplies contracts, tasks, and artifacts
        ▼
    ┌───────────────────────────────────────┐
    │ Researcher                            │
    │                                      │
    │ Authoritative professional evidence  │
    │ and job analysis                     │
    └──────────────────┬────────────────────┘
                       │
              analysis / evidence request
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
    ┌─────────────┐           ┌──────────────┐
    │ Writer      │           │ Interviewer  │
    │             │           │              │
    │ Presentation│           │ Human factual│
    │ authority   │           │ acquisition  │
    └──────┬──────┘           └──────┬───────┘
           │                         │
           │ resume                  │ evidence response
           ▼                         ▼
    ┌─────────────┐             Researcher
    │ Evaluator   │
    │             │
    │ Product     │
    │ judgment    │
    └─────────────┘

The human operator currently transfers information between these roles.

The Supervisor operates separately at the governance layer.

---

# 34. CURRENT V2 TASK MODEL

The intended task model is:

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

These task names represent kinds of work.

They do not represent workflow iterations.

Future changes to this task set should require a genuine difference in operation, not merely a different trigger or sequence position.

---

# 35. GOVERNING PRINCIPLE

The Rapid Resume System should remain understandable even if all transport technology is removed.

At its core, the system is:

> A set of specialized reasoning agents with explicit authority boundaries, communicating through structured artifacts, each performing a stable professional function against the current available information.

Current V2 should implement that conceptual system as simply as possible.

Future automation should make the system easier to operate.

It should not be required to explain how the system works.