# RAPID RESUME SYSTEM — AGENT CONTRACT STANDARD

**Template Version:** 2.0  
**System:** Rapid Resume System  
**Applies To:** All Rapid Resume System agents  
**Maintained By:** Supervisor  
**Status:** Active

---

# 1. PURPOSE

This document defines the required structure for all Rapid Resume System Agent Contracts.

An Agent Contract defines the durable reasoning role, responsibilities, authority, boundaries, inputs, outputs, decision rules, and completion conditions of an agent.

The contract should allow an agent to understand:

- Who it is.
- What professional function it performs.
- What outcomes it owns.
- What decisions it may make.
- What information it may rely on.
- What information it may produce.
- What it must not do.
- What responsibilities belong to other agents.
- When its work is complete.

Agent Contracts define **agent cognition and professional behavior**.

They do not define transport, orchestration, software lifecycle, message delivery, or connector implementation.

---

# 2. ARCHITECTURAL AUTHORITY

All Agent Contracts must conform to:

    resources/architecture-principles.md

When an Agent Contract conflicts with the Architecture Principles, the conflict must be identified and corrected.

The Agent Contract Standard governs contract structure.

The Architecture Principles govern system-level design.

The individual Agent Contract governs role-specific behavior within those boundaries.

The intended authority hierarchy is:

    Architecture Principles
            ↓
    Agent Contract Standard
            ↓
    Individual Agent Contract
            ↓
    Task Instructions
            ↓
    Structured Artifact Schemas

A lower-level artifact must not silently override a higher-level architectural rule.

---

# 3. TRANSPORT NEUTRALITY

Agent Contracts must remain usable when agents operate as bare conversational AI roles.

Contracts may define:

- Inputs.
- Outputs.
- Intended consumers.
- Human-interaction requirements.
- Information dependencies.
- Logical relationships with other agents.

Contracts must not depend on:

- Trello.
- Discord.
- Kanban.
- Cards.
- Lists.
- Inboxes.
- Automated routing.
- Python handlers.
- API connectors.
- Automated persistence.
- Workflow engines.
- Background workers.
- Event-driven orchestration.

For example, this is valid:

    Evidence Request
    Produced by: Researcher
    Intended consumer: Interviewer

This is implementation-specific and does not belong in the current contract:

    Move the card to the Interviewer queue.

The agent should understand the professional relationship between artifacts and agents without knowing how software transports them.

---

# 4. CONTRACT VERSUS TASK VERSUS SCHEMA

All Rapid Resume System artifacts must preserve the following separation.

## Contract

The contract defines durable agent behavior.

It answers:

- Who is this agent?
- What is its mission?
- What responsibilities does it own?
- What authority does it have?
- What information may it trust?
- What outputs may it produce?
- What must it never do?
- What belongs to another agent?
- When is its work complete?

Location:

    /agents/[agent]/contract.md

---

## Task Instruction

A Task Instruction defines one repeatable kind of work.

It answers:

- What operation is being performed?
- What inputs should be considered?
- What process should be followed?
- What outputs should be produced?
- What validation must occur?

Location:

    /agents/[agent]/tasks/[task-name].md

Task Instructions may specialize a contract.

They must not contradict or redefine the contract.

Different workflow conditions do not automatically require different task types.

---

## Schema

A schema defines the structure of a shared artifact.

It answers:

- What fields exist?
- Which fields are required?
- What values are permitted?
- Which identifiers connect artifacts?
- What structure must another agent or software consumer expect?

Location:

    /schemas/[schema-name].yaml

Schemas define data interfaces.

They do not define substantial agent behavior.

Contracts and tasks should reference schemas rather than reproducing them.

---

## Resource

A resource is shared material that agents may consume.

Examples include:

- Resume skeleton.
- Writing prompt bank.
- Architecture principles.
- Contract standards.
- Formatting requirements.
- Reference material.

Resources are neither behavior definitions nor structured data interfaces.

---

# 5. REQUIRED CONTRACT STRUCTURE

Every Agent Contract must use the following section order:

1. Role
2. Mission
3. Responsibilities
4. Authority
5. Inputs
6. Input Authority and Precedence
7. Outputs
8. Operating Principles
9. Role Boundaries
10. Decision Rules
11. Quality and Validation Requirements
12. Failure, Blocking, and Escalation Conditions
13. Completion Conditions
14. Prohibited Behaviors
15. Role-Specific Doctrine
16. Contract Interface

Section 15 may be minimal when no substantial role-specific doctrine is required.

All other sections are required unless the architecture explicitly provides an exception.

---

# 6. CONTRACT HEADER

Every contract begins with:

    # [AGENT NAME] AGENT CONTRACT

    **Contract Version:** [version]
    **Agent ID:** [stable-agent-id]
    **System:** Rapid Resume System
    **Contract Status:** [Active | Draft | Deprecated]

The Agent ID should remain stable across ordinary contract revisions.

The contract version refers to the contract itself, not the model, task, or system release.

---

# 7. SECTION 1 — ROLE

Define who the agent is within the Rapid Resume System.

State:

- Its professional function.
- Its fundamental responsibility.
- The primary question it exists to answer.
- What distinguishes it from adjacent agents.
- What it is explicitly not.

This section establishes identity.

It should not become a procedural task description.

A strong Role section should allow a reader to answer:

> Why does this agent exist as a separate role?

---

# 8. SECTION 2 — MISSION

Define the outcome the agent is responsible for producing for the system.

The Mission describes the desired end state rather than the specific process.

A strong Mission answers:

> What must be true when this agent has successfully performed its role?

The Mission should remain stable across different task instructions.

---

# 9. SECTION 3 — RESPONSIBILITIES

Define the persistent professional functions owned by the agent.

Responsibilities describe what the agent owns regardless of which specific task is currently being performed.

Use a numbered list.

Responsibilities should:

- Be durable.
- Establish accountability.
- Remain inside the agent's domain.
- Avoid unnecessary duplication with other roles.
- Avoid describing one invocation-specific sequence.
- Reflect the current Architecture Principles.

A responsibility is not automatically authority.

For example:

    Responsibility:
    Identify evidence gaps.

does not necessarily imply:

    Authority:
    Directly interview the job hunter.

Those may belong to different agents.

---

# 10. SECTION 4 — AUTHORITY

Define which decisions and actions the agent may perform independently.

Use three subsections.

## The Agent May

Define discretionary authority.

Examples:

- Analyze.
- Classify.
- Select.
- Compose.
- Evaluate.
- Request.
- Produce.
- Recommend.

## The Agent Must

Define mandatory behavior that applies whenever relevant.

Examples:

- Preserve factual provenance.
- Consider all supplied relevant artifacts.
- Preserve uncertainty.
- Validate output.

## The Agent Must Not

Define explicit authority boundaries.

Examples:

- Modify another agent's authoritative data.
- Invent professional evidence.
- Override another agent's owned judgment.
- Expand beyond evidence authorization.

Authority should answer:

> What may this agent decide without asking another agent or the human operator for professional judgment?

The contract should provide enough authority for the agent to perform its role without absorbing other roles.

---

# 11. SINGLE AUTHORITATIVE OWNERSHIP

Contracts must respect the system principle that every material mutable information domain or professional judgment should have one authoritative owner.

Current authoritative ownership includes:

    Professional evidence state
    → Researcher

    Human evidence acquisition
    → Interviewer

    Resume and cover-letter presentation
    → Writer

    Product screening judgment
    → Evaluator

    System architecture and governance
    → Supervisor

Contracts must not silently grant overlapping primary ownership.

Other agents may:

- Read.
- Comment.
- Identify deficiencies.
- Supply evidence.
- Request reconsideration.

They must not independently mutate another agent's authoritative domain unless the Architecture Principles explicitly permit it.

---

# 12. SECTION 5 — INPUTS

Define what information and artifacts the agent may consume.

Use:

## Required Inputs

Inputs without which the relevant role or task cannot meaningfully proceed.

## Optional Inputs

Inputs that may improve reasoning or provide additional context.

Inputs should be described by artifact type or information type rather than transport source.

For example:

    - Current Job Experience Analysis.
    - Evidence Response.
    - Target Job Description.
    - Previous evaluation.

Avoid implementation-specific descriptions such as:

    - Card attachment.
    - Discord message.
    - Trello comment.

For structured inputs, reference the authoritative schema when one exists.

Example:

    Evidence Response
    Schema: /schemas/evidence-response.yaml

Do not reproduce the entire schema in the contract.

---

# 13. SECTION 6 — INPUT AUTHORITY AND PRECEDENCE

Define how the agent should interpret inputs when they differ in authority or conflict.

This section should identify:

- Which sources establish factual truth.
- Which sources establish target requirements.
- Which sources authorize claims.
- Which sources provide historical context.
- Which sources provide feedback.
- Which sources may be reconsidered.
- Which sources must not be silently overridden.

Use separate precedence rules when different questions have different authorities.

For example:

    Target requirement authority
    and
    professional evidence authority

may have different precedence orders.

When sources conflict:

- Preserve the conflict.
- Follow the defined authority rules.
- Do not select whichever interpretation produces the most attractive outcome.
- Request clarification when the authoritative agent cannot safely resolve the conflict.

---

# 14. DOWNSTREAM FEEDBACK

Contracts must preserve the principle of downstream deficiency authority.

When a downstream agent identifies a deficiency within its owned domain, the upstream agent must treat that deficiency as requiring resolution.

The upstream agent retains authority over the solution inside its own domain.

Example:

    Evaluator:
    The resume does not adequately demonstrate requirement X.

The Researcher or Writer should not adjudicate whether the Evaluator's screening judgment was correct.

They should determine how to resolve the deficiency within their own authority.

Likewise, the Evaluator must not dictate the specific upstream solution.

Contracts should distinguish:

    Deficiency authority
    from
    solution authority

This prevents circular agent disagreement.

---

# 15. SECTION 7 — OUTPUTS

Define what artifacts and judgments the agent may produce.

Use:

## Primary Outputs

Outputs normally produced when the agent successfully performs its role.

## Conditional Outputs

Outputs created only when defined conditions occur.

Examples:

- Evidence Request.
- Process Feedback.
- Blocking issue.
- Revision recommendation.
- Unsupported-requirement finding.

## Intended Consumers

Identify which agent or human role logically consumes each output.

Example:

    Job Experience Analysis
    Intended consumer: Writer

    Evidence Request
    Intended consumer: Interviewer

This expresses logical interface relationships.

It does not define transport.

For structured outputs, reference the authoritative schema.

---

# 16. PROCESS FEEDBACK

Contracts may authorize an execution agent to produce Process Feedback when it identifies recurring or material system friction.

Examples include:

- Contract ambiguity.
- Task ambiguity.
- Schema weakness.
- Missing information patterns.
- Repeated role confusion.
- Repeated avoidable rework.
- Repeated evidence deficiencies caused by system structure.

Process Feedback is a secondary system-governance artifact.

Its intended consumer is the Supervisor.

The contract must not assume how Process Feedback reaches the Supervisor.

Current V2 may rely on manual transfer by the human operator.

---

# 17. SECTION 8 — OPERATING PRINCIPLES

Define permanent reasoning principles governing the agent across all tasks.

Operating Principles explain **how the agent should think**.

Examples:

- Capability over billet.
- Visible evidence governs screening.
- Evidence before narrative.
- Collaborative evidence discovery.
- Preserve provenance.
- Relevance over prestige.
- Simplification without distortion.

Operating Principles should not contain detailed task procedures.

If a rule answers:

> What should the agent always value or preserve?

it likely belongs here.

If it answers:

> What steps should the agent execute for this task?

it likely belongs in the Task Instruction.

---

# 18. SECTION 9 — ROLE BOUNDARIES

Explicitly define how the agent differs from adjacent agents.

Use:

## This Agent Owns

List this agent's authoritative professional functions.

Then identify relevant adjacent agents and their ownership.

Example:

## Researcher Owns

- Evidence retrieval.
- Evidence reconciliation.
- Job Experience Record custody.

## Interviewer Owns

- Human questioning.
- Evidence confirmation.

Only include roles relevant to the boundary being explained.

Role boundaries should make clear when the agent must stop because another agent owns the next professional decision.

Contracts should not describe transport or automated routing.

---

# 19. SECTION 10 — DECISION RULES

Define recurring judgments the agent must make and the criteria governing those decisions.

Examples:

- Evidence ranking.
- Requirement scoring.
- Gap classification.
- Direct versus transferable evidence.
- Claim authorization.
- Functional-role classification.
- Submission readiness.
- Evidence sufficiency.

Decision Rules should be deterministic wherever practical.

When judgment remains subjective, define:

- Relevant criteria.
- Evidence requirements.
- Confidence expectations.
- How uncertainty should be represented.

Decision Rules should not depend on implementation details.

---

# 20. TASK IDENTITY AND CURRENT-STATE REASONING

Contracts should support task instructions that represent **kinds of work**, not iteration states.

Avoid designing authority around separate concepts such as:

- initial.
- revised.
- rechecked.
- reevaluated.
- returned.
- second pass.

when the professional operation is materially the same.

Agents should generally reason against the complete current artifact set.

Previous outputs may be inputs.

They are not automatically immutable conclusions.

Contracts should support reconsideration when:

- New evidence appears.
- New feedback appears.
- A prior interpretation is shown to be insufficient.
- Current authoritative artifacts change.

---

# 21. IDEMPOTENT TASK SUPPORT

Where applicable, contracts should support idempotent task behavior.

Given materially identical:

- Inputs.
- Evidence.
- Feedback.
- Constraints.

the agent should converge on materially stable judgments.

Contracts should discourage:

- Novelty for novelty's sake.
- Arbitrary reprioritization.
- New criticism without new basis.
- Rewriting already optimal content without reason.

Idempotence concerns material decisions rather than token-for-token identical language.

---

# 22. SECTION 11 — QUALITY AND VALIDATION REQUIREMENTS

Define what the agent must verify before treating its work as complete.

Use:

## Common Validation Requirements

Include relevant checks such as:

- Required inputs were available or missing inputs were identified.
- Required outputs were produced.
- Structured outputs conform to schemas.
- The agent remained within its authority.
- Factual claims remain supported.
- Provenance was preserved.
- Attribution was preserved.
- Uncertainty was disclosed.
- Unsupported assumptions were not introduced.

## Agent-Specific Validation Requirements

Add checks unique to the role.

Validation should test the quality of the reasoning product.

It should not depend on a future workflow implementation.

Avoid language such as:

    before moving the card

or:

    before leaving the Kanban stage

Prefer:

    before completing the task

or:

    before treating the output as complete

---

# 23. SECTION 12 — FAILURE, BLOCKING, AND ESCALATION CONDITIONS

Define situations in which the agent cannot safely or correctly complete its normal output.

Examples:

- Required input missing.
- Conflicting evidence.
- Insufficient factual support.
- Invalid schema.
- Unsupported requested claim.
- Human confirmation required.
- Another agent owns the unresolved professional decision.

For each condition define:

- Condition.
- Required response.
- Additional artifact or information needed.
- Appropriate authoritative role, when relevant.

Use logical ownership rather than transport instructions.

For example:

    Additional factual evidence required.

    Response:
    Researcher produces an Evidence Request.

    Intended consumer:
    Interviewer.

Do not specify how the request is transmitted.

---

# 24. ESCALATION IS NOT ROUTING

In this standard, escalation means:

> The current agent has reached a professional boundary and identifies which authority is required next.

It does not mean:

> The agent controls workflow transport.

For example:

    Writer determines that authorized evidence is insufficient.

The Writer may identify:

    Researcher review required.

The contract should not assume whether the human operator, a future handler, or another system component performs the transfer.

---

# 25. SECTION 13 — COMPLETION CONDITIONS

Define the agent's **Definition of Done**.

Completion Conditions describe what must be true before the agent considers its professional work complete.

These conditions should be:

- Observable.
- Testable where practical.
- Independent of transport implementation.

Examples:

- Every material requirement has been evaluated.
- Every material claim is traceable.
- Human confirmation has been obtained.
- Evidence gaps are explicit.
- Required structured outputs are complete.

The agent must not declare completion merely because it generated text.

Completion is based on satisfying the professional quality standard.

---

# 26. SECTION 14 — PROHIBITED BEHAVIORS

Define hard constraints that apply regardless of task.

Use this section only for behavior that is genuinely prohibited.

Examples:

- Never fabricate professional experience.
- Never manufacture metrics.
- Never change employer provenance.
- Never override another agent's authoritative data.
- Never represent transferable evidence as direct evidence without support.

Do not use this section for ordinary preferences.

Prohibitions should be durable across tasks.

---

# 27. SECTION 15 — ROLE-SPECIFIC DOCTRINE

Use this section for substantial conceptual guidance unique to the role.

Examples:

## Researcher

- Capability Over Billet.
- Career-Wide Evidence Retrieval.
- Evidence Custody.
- Functional Translation.
- Transferability Discipline.

## Interviewer

- Collaborative Interview Posture.
- Memory Development.
- Evidence Confirmation.
- Evidence Acquisition Versus Evidence Reconciliation.

## Writer

- Professional Translation.
- Employment Envelope.
- Functional Placement.
- Evidence Before Language.

## Evaluator

- Two-Pass Evaluation.
- Three Screening Perspectives.
- Visibility Versus Validity.
- Skepticism Without Cynicism.

## Supervisor

- Governance Versus Execution.
- Kaizen.
- Architectural Conformance.
- Controlled Evolution.

Role-Specific Doctrine may be detailed.

It must remain durable role behavior rather than task-specific procedure.

---

# 28. SECTION 16 — CONTRACT INTERFACE

Provide a concise logical summary of the agent's interface with the rest of the system.

The Contract Interface is **not** a workflow implementation specification.

Use the following structure.

## Accepts

List artifact or information types the agent may consume.

Example:

    Target Job Description
    Job Experience Records
    Evidence Responses

## Produces

List primary and conditional artifacts the agent may create.

Example:

    Job Experience Analysis
    Evidence Request
    Process Feedback

## Intended Consumers

Identify the logical consumer of each produced artifact.

Example:

    Job Experience Analysis
    → Writer

    Evidence Request
    → Interviewer

    Process Feedback
    → Supervisor

The arrow indicates intended information flow, not automated routing.

## May Require

Identify information the agent may determine is necessary but which belongs to another authority.

Example:

    Additional factual evidence
    Authority: Interviewer

## Human Interaction

Specify:

    None

or:

    Permitted

or:

    Required

Then define the professional circumstances.

Do not specify the communication technology.

---

# 29. HUMAN INTERACTION

Human interaction is a role capability, not a transport implementation.

Examples:

The Interviewer may require direct interaction with the job hunter.

The Supervisor may collaborate directly with the System Owner.

Contracts may define:

- Why human interaction is required.
- What information may be requested.
- What confirmation is necessary.
- What authority the human retains.

Contracts must not define:

- Discord.
- Email.
- Chat platform.
- Webhook.
- Notification technology.

Those belong to future implementation layers.

---

# 30. EVIDENCE-CUSTODY COMPATIBILITY

All contracts must preserve Researcher authority over the professional evidence model.

The Researcher owns:

- Job Experience Record creation.
- Job Experience Record modification.
- Evidence integration.
- Evidence reconciliation.
- Record merging.
- Record splitting.
- Provenance maintenance.

The Interviewer may produce confirmed factual Evidence Responses.

The Writer and Evaluator may identify evidence deficiencies.

Neither independently modifies authoritative professional evidence.

Contracts that violate this principle are architecturally non-conformant.

---

# 31. EVIDENCE-REQUEST COMPATIBILITY

New human evidence acquisition should pass logically through the Researcher.

Writer or Evaluator may identify a deficiency.

Researcher determines whether:

- Existing evidence resolves it.
- Analysis or prioritization should change.
- New factual evidence is required.

When new factual evidence is required:

    Researcher produces Evidence Request

    Intended consumer:
    Interviewer

The Interviewer investigates and produces an Evidence Response.

The Researcher then determines how the response affects authoritative evidence.

Agent Contracts should preserve this division.

---

# 32. FACTUAL INTEGRITY

Every contract must preserve factual integrity as a higher priority than optimization.

No agent may improve apparent job fit by:

- Inventing evidence.
- Inventing results.
- Inventing metrics.
- Inventing ownership.
- Inventing scope.
- Inventing tools.
- Inventing qualifications.
- Changing employer provenance.
- Changing employment relationships.
- Converting transferable evidence into direct evidence without support.
- Converting participation into ownership.

When evidence is insufficient, the limitation must remain visible to the appropriate authoritative agent.

---

# 33. PROVENANCE VERSUS PRESENTATION

Contracts should preserve the distinction between:

    Provenance
    = where and when experience occurred

    Professional capability
    = what the experience demonstrates

    Functional classification
    = the recognizable professional function represented

    Presentation
    = how authorized evidence is communicated

The Researcher owns evidence provenance and functional classification.

The Writer owns presentation.

A contract must not confuse these domains.

---

# 34. PROCESS FEEDBACK AND KAIZEN

Execution-agent contracts may authorize Process Feedback.

Supervisor contracts may authorize:

- Process-feedback analysis.
- Pattern identification.
- Root-cause analysis.
- Draft contract changes.
- Draft task changes.
- Draft schema changes.
- Architecture recommendations.

The Supervisor may propose changes.

The System Owner retains approval authority over adoption into the active system.

Current contracts should not assume automated feedback collection or automated repository modification.

---

# 35. CURRENT-SCOPE TEST

Before approving a contract, ask:

> Could this contract still function if Trello, Discord, Kanban, Python handlers, connectors, APIs, and automated routing did not exist?

If the answer is no, determine whether implementation-specific assumptions have leaked into the contract.

Current V2 contracts should remain functional when:

- The contract is pasted into an AI conversation.
- The task instruction is pasted into the same conversation.
- Relevant artifacts are supplied manually.
- Outputs are manually transferred by the human operator.

---

# 36. CONTRACT AUTHORING RULES

When creating or revising an Agent Contract:

1. Follow the required section order.
2. Conform to `resources/architecture-principles.md`.
3. Keep identity separate from procedure.
4. Keep responsibilities separate from authority.
5. Grant enough authority for the agent to perform its professional role.
6. Preserve single authoritative ownership.
7. Define input authority and precedence explicitly.
8. Reference schemas rather than duplicating them.
9. Keep transport mechanisms out of the contract.
10. Preserve Researcher evidence custody.
11. Preserve Interviewer evidence-acquisition boundaries.
12. Preserve Writer presentation authority.
13. Preserve Evaluator product-judgment authority.
14. Preserve Supervisor governance authority.
15. Respect downstream deficiency authority.
16. Do not let one agent dictate another agent's owned solution.
17. Support current-state reasoning.
18. Support idempotent tasks where appropriate.
19. Put permanent reasoning doctrine in the contract.
20. Put invocation-specific procedure in task instructions.
21. Put structured data definitions in schemas.
22. Prefer observable rules over vague quality language.
23. Preserve factual integrity.
24. Make logical consumers explicit without specifying transport.
25. Ensure the contract can be understood without hidden conversational context.

---

# 37. SUPERVISOR CONTRACT REVIEW CHECKLIST

Before approving a new or revised contract, the Supervisor should verify:

- [ ] The contract conforms to the current Architecture Principles.
- [ ] The required section order is followed.
- [ ] The Role clearly identifies why the agent exists.
- [ ] The Mission defines a stable desired outcome.
- [ ] Responsibilities are persistent rather than task-specific.
- [ ] Authority is explicit.
- [ ] Responsibilities and authority are not confused.
- [ ] Required and optional inputs are identified.
- [ ] Input authority and precedence are defined.
- [ ] Outputs are explicit.
- [ ] Intended consumers are identified.
- [ ] Operating Principles describe durable reasoning doctrine.
- [ ] Role Boundaries clearly distinguish adjacent agents.
- [ ] Single authoritative ownership is preserved.
- [ ] Researcher evidence custody is preserved.
- [ ] Interviewer evidence acquisition is separated from reconciliation.
- [ ] Writer presentation authority is preserved.
- [ ] Evaluator product-judgment authority is preserved.
- [ ] Supervisor governance remains separate from execution.
- [ ] Downstream deficiency authority is respected.
- [ ] Decision Rules cover recurring material judgments.
- [ ] Validation requirements test professional output quality.
- [ ] Failure and blocking conditions identify the appropriate authority.
- [ ] Completion Conditions create a clear Definition of Done.
- [ ] Prohibited Behaviors contain only hard constraints.
- [ ] Role-Specific Doctrine does not become task procedure.
- [ ] Contract Interface is logical rather than transport-specific.
- [ ] Shared schemas are referenced rather than duplicated.
- [ ] Task instructions have not leaked into the contract.
- [ ] Trello, Discord, Kanban, handler, connector, or routing assumptions are absent.
- [ ] Human interaction is defined independently of communication technology.
- [ ] The contract supports current-state reasoning.
- [ ] The contract does not require iteration-specific task modes.
- [ ] The contract supports idempotence where applicable.
- [ ] The agent can operate from explicitly supplied artifacts without hidden context.
- [ ] The contract does not depend on future infrastructure.

---

# 38. ARCHITECTURAL CONFORMANCE FAILURE

A contract should be considered architecturally non-conformant when it:

- Grants conflicting ownership over authoritative data.
- Allows Interviewer to independently modify authoritative Job Experience Records.
- Allows Writer or Evaluator to bypass Researcher for new evidence acquisition.
- Gives an agent authority to override another agent's owned judgment.
- Encodes workflow-state-specific behavior as permanent role identity.
- Depends on Trello, Discord, Kanban, Python handlers, connectors, or automated routing.
- Embeds full shared schemas unnecessarily.
- Requires hidden conversational context.
- Confuses professional reasoning with software transport.
- Weakens factual integrity to improve apparent fit.

Architectural non-conformance should be corrected at the owning design layer rather than worked around in lower-level task instructions.

---

# 39. STANDARD OF COMPLETION

An Agent Contract conforming to this standard should allow a human or AI reader to answer:

    Who is this agent?

    Why does it exist?

    What professional outcome does it own?

    What decisions may it make?

    What information may it trust?

    What artifacts may it consume?

    What artifacts may it produce?

    Who logically consumes those outputs?

    What decisions belong to other agents?

    What must it never do?

    How does it make recurring judgments?

    How does it validate its work?

    What happens when required information is missing?

    When is the work professionally complete?

If those questions can be answered without knowing anything about Trello, Discord, Kanban, Python handlers, API connectors, or automated workflow infrastructure, the contract is properly separated from implementation.