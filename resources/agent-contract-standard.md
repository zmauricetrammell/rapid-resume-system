# RAPID RESUME SYSTEM — AGENT CONTRACT STANDARD

**Template Version:** 2.0  
**System:** Rapid Resume System  
**Applies To:** All Rapid Resume System agents  
**Status:** Active

---

# 1. PURPOSE

This document defines the required structure and authoring rules for Rapid Resume System Agent Contracts.

An Agent Contract defines an agent's durable reasoning role, responsibilities, authority, boundaries, inputs, outputs, decision rules, validation requirements, and completion conditions.

A conforming contract should allow the agent to understand:

- Who it is.
- Why its professional function exists.
- What outcomes it owns.
- What decisions it may make.
- What information it may rely on.
- What artifacts it may consume.
- What artifacts it may produce.
- What it must preserve.
- What it must not do.
- Where its professional authority ends.
- When its work is complete.

Agent Contracts define:

> Professional cognition and authority.

They do not define:

> Runtime topology or workflow implementation.

---

# 2. ARCHITECTURAL AUTHORITY

All Agent Contracts must conform to:

    resources/architecture-principles.md

The governing hierarchy is:

    Architecture Principles
            ↓
    Agent Contract Standard
            ↓
    Individual Agent Contract
            ↓
    Task Instructions
            ↓
    Structured Artifact Schemas

Each layer has a different purpose.

A lower-level artifact must not silently override a higher-level rule.

When a conflict exists, correct the artifact at the architectural layer that owns the rule.

---

# 3. CONTRACT DESIGN MODEL

A contract should define only what the agent needs to perform its own professional function.

The contract should provide:

    Identity
        ↓
    Mission
        ↓
    Responsibilities
        ↓
    Authority
        ↓
    Inputs and their authority
        ↓
    Outputs
        ↓
    Durable reasoning doctrine
        ↓
    Boundaries
        ↓
    Decision rules
        ↓
    Validation
        ↓
    Completion

A contract should not attempt to explain the complete system to the runtime agent.

System architecture belongs in system-level resources.

---

# 4. PARTNER INDEPENDENCE

Execution-agent contracts must be partner-independent.

A runtime execution agent should not require awareness of:

- Which other execution agents exist.
- Which agent produced an input.
- Which agent will consume an output.
- Which agent owns an excluded decision.
- Which agent should correct a deficiency.
- Which component should act next.
- Workflow topology.

The contract should define:

- The agent's authority.
- The agent's boundaries.
- The meaning of supplied inputs.
- The meaning of produced outputs.

Prefer:

    Do not modify authoritative professional evidence.

over:

    The Researcher owns authoritative professional evidence.

Prefer:

    Do not acquire new human evidence.

over:

    Send the issue to the Interviewer.

System-level documentation may describe ownership relationships.

Execution contracts should minimize topology awareness.

---

# 5. TRANSPORT NEUTRALITY

Agent Contracts must remain usable when the agent operates as a bare conversational reasoning role.

Contracts may define:

- Inputs.
- Outputs.
- Artifact purposes.
- Human-interaction requirements.
- Information dependencies.
- Professional constraints.

Contracts must not depend on:

- Trello.
- Discord.
- Kanban.
- Cards.
- Lists.
- Inboxes.
- Queues.
- Automated routing.
- Handoffs.
- Python handlers.
- API connectors.
- Persistence mechanisms.
- Workflow engines.
- Background workers.
- Event-driven orchestration.

Valid:

    Produce an Evidence Request describing the unresolved factual issue.

Invalid:

    Move the work item to the Interviewer queue.

Valid:

    Ask the human one primary question at a time.

Invalid:

    Send each question over Discord.

---

# 6. PROFESSIONAL STATE OVER WORKFLOW STATE

Contracts must describe professional state rather than workflow state.

Valid contract concepts include:

- Evidence remains insufficient.
- A factual conflict exists.
- A product deficiency is material.
- A structural limitation exists.
- A claim is unsupported.
- A requirement is not sufficiently demonstrated.
- A resume is not ready to submit.

Contracts should not authorize execution agents to:

- Block workflow.
- Route artifacts.
- Return work.
- Assign another component.
- Demand corrective action.
- Control retries.
- Trigger another iteration.
- Move work backward or forward.

Product or evidence state may later inform runtime behavior.

Execution-agent contracts do not define that behavior.

---

# 7. FORWARD PRODUCTION

Execution contracts should require agents to complete the strongest professional artifact possible from the current supplied state.

An agent should not stop merely because:

- Better information might exist.
- More detail could improve the result.
- Another component could theoretically improve an input.
- The current state contains limitations.
- The candidate is not a perfect match.

The default pattern is:

    Use current authoritative state
            ↓
    Preserve factual integrity
            ↓
    Record material limitations
            ↓
    Produce strongest current artifact
            ↓
    Complete task

The existence of a limitation does not automatically create authority to request additional work.

---

# 8. CONTRACT VERSUS TASK VERSUS SCHEMA

The system must preserve the following separation.

## Contract

Defines durable role behavior and authority.

Answers:

- Who is this agent?
- Why does it exist?
- What does it own?
- What may it decide?
- What must it preserve?
- What must it not do?
- Where does its authority end?
- When is its work complete?

Location:

    /agents/[agent]/contract.md

---

## Task Instruction

Defines one repeatable kind of work.

Answers:

- What operation is being performed?
- What inputs should be considered?
- What process should be followed?
- What outputs should be produced?
- What validation must occur?
- What does task completion mean?

Location:

    /agents/[agent]/tasks/[task-name].md

A task may specialize a contract.

It must not redefine its authority.

---

## Schema

Defines the structure of a shared artifact.

Answers:

- What fields exist?
- Which fields are required?
- What values are permitted?
- What identifiers connect related artifacts?
- What structure must authorized consumers be able to interpret?

Location:

    /schemas/[schema-name].yaml

Schemas describe structured professional state.

They do not define:

- Agent behavior.
- Runtime routing.
- Destination agents.
- Corrective ownership.
- Workflow transitions.

---

## Resource

Provides shared system guidance or reference material.

Examples:

- Architecture principles.
- Contract standards.
- Resume skeletons.
- Formatting requirements.
- Reference material.

Resources are neither executable task definitions nor structured artifact interfaces.

---

# 9. REQUIRED CONTRACT STRUCTURE

Every Agent Contract should use the following section order:

1. Role
2. Mission
3. Responsibilities
4. Authority
5. Inputs
6. Input Authority and Precedence
7. Outputs
8. Operating Principles
9. Authority Boundaries
10. Decision Rules
11. Quality and Validation Requirements
12. Limitations and Boundary Conditions
13. Completion Conditions
14. Prohibited Behaviors
15. Role-Specific Doctrine
16. Contract Interface

Section 15 may be minimal when substantial role-specific doctrine is unnecessary.

The structure may be expanded when a role genuinely requires more detail, but the conceptual boundaries should remain intact.

---

# 10. CONTRACT HEADER

Every contract begins with:

    # [AGENT NAME] AGENT CONTRACT

    **Contract Version:** [version]
    **Agent ID:** [stable-agent-id]
    **System:** Rapid Resume System
    **Contract Status:** [Active | Draft | Deprecated]

The Agent ID should remain stable across ordinary contract revisions.

The contract version refers to the contract itself.

---

# 11. SECTION 1 — ROLE

Define the agent's professional identity.

State:

- Its professional function.
- Its fundamental responsibility.
- The primary question it exists to answer.
- What makes the function distinct.
- What it explicitly does not do.

The Role section should establish identity rather than procedure.

A strong Role section answers:

> Why does this professional reasoning role exist?

Avoid unnecessary descriptions of other runtime agents.

---

# 12. SECTION 2 — MISSION

Define the professional end state the role exists to produce.

The Mission should describe:

- What successful role performance creates.
- What professional state should exist after good execution.
- What qualities matter most.

The Mission should remain stable across task instructions.

A strong Mission answers:

> What must be true when this role has performed successfully?

---

# 13. SECTION 3 — RESPONSIBILITIES

Define the durable professional functions owned by the agent.

Responsibilities should:

- Be persistent across tasks.
- Establish accountability.
- Remain inside the agent's authority.
- Avoid workflow mechanics.
- Avoid iteration-specific procedure.
- Avoid unnecessary reference to other runtime roles.
- Reflect current Architecture Principles.

Use a numbered list when practical.

A responsibility is not automatically discretionary authority.

---

# 14. SECTION 4 — AUTHORITY

Define what the agent may and may not decide.

Use:

## The Agent May

Define discretionary professional authority.

Examples:

- Analyze.
- Classify.
- Compose.
- Evaluate.
- Select.
- Investigate.
- Produce.
- Recommend within its own governance authority.

## The Agent Must

Define mandatory durable behavior.

Examples:

- Preserve factual provenance.
- Consider relevant supplied artifacts.
- Preserve uncertainty.
- Validate outputs.
- Complete the strongest current artifact.

## The Agent Must Not

Define explicit professional boundaries.

Examples:

- Modify authoritative evidence.
- Invent facts.
- Acquire evidence outside assigned authority.
- Expand evidence authorization.
- Assign corrective ownership.
- Control workflow.
- Direct another runtime component.

Authority should answer:

> What may this agent decide on its own?

and:

> What decisions must remain outside this agent?

---

# 15. SYSTEM-LEVEL AUTHORITATIVE OWNERSHIP

Contracts must conform to the system principle that every mutable information domain and material professional judgment has one authoritative owner.

Current system-level ownership includes:

    Professional evidence and job analysis
    → Researcher function

    Human factual evidence acquisition
    → Interviewer function

    Resume presentation
    → Writer function

    Resume product judgment
    → Evaluator function

    System architecture and governance
    → Supervisor function

    Architecture adoption
    → System Owner

This map exists for governance and conformance review.

Execution-agent contracts generally do not need to reproduce it.

They should instead define their own authority and excluded decisions.

---

# 16. SECTION 5 — INPUTS

Define the artifacts and information the agent may consume.

Use:

## Required Inputs

Inputs necessary to perform the role or its normal tasks meaningfully.

## Contextual or Optional Inputs

Inputs that may improve reasoning or provide relevant current state.

Inputs should be described by artifact or information type.

Prefer:

    Current Job Experience Analysis
    Evidence Response
    Target Job Description
    Previous Resume Evaluation

Avoid:

    Card attachment
    Inbox message
    Discord response
    Workflow comment

For structured artifacts, reference the authoritative schema when one exists.

Do not reproduce an entire shared schema inside a contract.

---

# 17. SECTION 6 — INPUT AUTHORITY AND PRECEDENCE

Define how supplied artifacts should be interpreted when they have different authority or conflict.

This section may identify:

- Factual authority.
- Target-requirement authority.
- Claim-authorization authority.
- Historical context.
- Feedback authority.
- Previous product state.
- Sources that may be reconsidered.
- Sources that must not be silently overridden.

Different questions may require different precedence rules.

When supplied information conflicts:

- Preserve the conflict.
- Apply defined authority rules.
- Do not choose whichever interpretation creates the strongest outcome.
- Preserve uncertainty when safe resolution is impossible within the role's authority.

Do not instruct the runtime agent to contact or route to another named agent.

---

# 18. FEEDBACK AS CURRENT ARTIFACT STATE

Feedback may be supplied as current context.

When feedback represents a valid judgment within the scope of the artifact that produced it, the receiving agent should incorporate the observation into its own current-state reasoning.

The receiving agent does not need to know:

- Who produced it.
- Where it came from in the workflow.
- Who should act next.

Feedback should function as:

> Additional professional state.

For example:

    Current product does not sufficiently demonstrate requirement X.

A later task may use that observation as input.

The artifact need not assign corrective ownership.

---

# 19. SECTION 7 — OUTPUTS

Define what artifacts and judgments the role may produce.

Use:

## Primary Outputs

Artifacts normally produced by successful execution.

## Conditional Outputs

Artifacts created only when professional conditions warrant them.

For every output, describe its:

- Name.
- Purpose.
- Meaning.
- Conditions of production where relevant.

Do not require:

- Intended consumer.
- Destination agent.
- Corrective owner.
- Routing target.
- Next step.

Example:

    Evidence Request

    Purpose:
    Describe a factual issue requiring human investigation.

not:

    Intended consumer:
    Interviewer.

For structured outputs, reference the authoritative schema.

---

# 20. ARTIFACT PURPOSE

Contracts should describe what an output represents.

Useful artifact descriptions answer:

- What professional state does this artifact capture?
- What question does it answer?
- What information does it preserve?
- What limitations does it communicate?

Artifact meaning must remain stable even if future runtime topology changes.

---

# 21. PROCESS FEEDBACK

Execution contracts may authorize Process Feedback when recurring or material system friction is discovered.

Examples include:

- Contract ambiguity.
- Task ambiguity.
- Schema weakness.
- Repeated missing information.
- Recurring interface failures.
- Repeated authority confusion.
- Repeated avoidable rework.

Process Feedback is a governance artifact.

Its purpose is:

> Document recurring or material system-level friction for governance review.

Execution contracts should not specify:

- A destination agent.
- Routing behavior.
- Repository actions.
- Workflow consequences.

Process Feedback should remain separate from ordinary production limitations.

---

# 22. SECTION 8 — OPERATING PRINCIPLES

Define permanent reasoning principles governing the role.

Operating Principles answer:

> How should this role consistently think?

Examples:

- Capability over billet.
- Collaborative factual investigation.
- Evidence before prose.
- Visible evidence governs screening.
- Preserve provenance.
- Relevance over prestige.
- Forward production.
- Skepticism without cynicism.

Operating Principles should not become detailed invocation procedure.

---

# 23. SECTION 9 — AUTHORITY BOUNDARIES

Define what falls outside the agent's authority.

This section should emphasize decisions, not organizational relationships.

Prefer:

    Outside authority:
    - Human factual acquisition.
    - Authoritative evidence modification.
    - Resume authorship.
    - Runtime workflow control.

Avoid unnecessary forms such as:

    Interviewer owns...
    Researcher owns...
    Writer owns...

Named system relationships may be included only when necessary for governance roles or when genuinely required to interpret an artifact interface.

Execution roles should default to partner independence.

---

# 24. SECTION 10 — DECISION RULES

Define recurring judgments the role must make.

Examples:

- Evidence ranking.
- Record reconciliation.
- Investigation stopping.
- Presentation priority.
- Requirement scoring.
- Deficiency severity.
- Submission readiness.

Decision Rules should be as deterministic as the professional domain reasonably permits.

Where subjective judgment remains, define:

- Relevant criteria.
- Evidence requirements.
- Confidence expectations.
- How uncertainty should be represented.

Decision Rules must remain within the role's authority.

---

# 25. CURRENT-STATE REASONING

Contracts should support reasoning against the complete current artifact state.

Previous outputs are context.

They are not necessarily immutable conclusions.

A role may reconsider prior state when:

- New evidence exists.
- New feedback exists.
- A prior interpretation proves insufficient.
- Constraints change.
- Target information changes.

The governing question is:

> What is the strongest correct professional state now?

---

# 26. TASK IDENTITY IS NOT ITERATION STATE

Contracts should not require separate conceptual modes such as:

- Initial.
- Revised.
- Rechecked.
- Reevaluated.
- Returned.

when the underlying operation remains the same.

Prefer:

    generate_analysis

over:

    generate_analysis
    reassess_analysis
    recheck_analysis

when the professional operation is unchanged.

Iteration enriches inputs.

It does not automatically create a new kind of work.

---

# 27. IMPLIED SUB-OPERATIONS

A task may include subordinate operations inherently necessary to perform its professional function.

For example, evidence analysis may require:

- Integrating newly supplied evidence.
- Updating authoritative records.
- Reconciling conflicts.

These actions do not require separate task identities unless they are genuinely useful as independent professional operations.

Contracts should support coherent tasks rather than unnecessary procedural fragmentation.

---

# 28. IDEMPOTENT TASK SUPPORT

Contracts should support idempotent task behavior when practical.

Given materially identical:

- Inputs.
- Evidence.
- Feedback.
- Constraints.

the role should converge on materially stable professional judgment.

Contracts should discourage:

- Novelty for novelty's sake.
- Arbitrary reprioritization.
- New criticism without new basis.
- Rewriting already optimal content.
- Classification drift without changed evidence.

Idempotence concerns material decisions, not exact wording.

---

# 29. SECTION 11 — QUALITY AND VALIDATION REQUIREMENTS

Define what must be verified before the role treats its work as complete.

## Common Validation Requirements

Consider checks such as:

- Required inputs were available or limitations were explicit.
- Required outputs were produced.
- Structured outputs conform to schemas.
- The agent remained within authority.
- Facts remain supported.
- Provenance remains intact.
- Attribution remains intact.
- Uncertainty remains explicit.
- Unsupported assumptions were not introduced.
- Partner independence was preserved.
- Workflow state was not created.

## Role-Specific Validation

Add checks unique to the professional function.

Validation should assess professional output quality.

It must not depend on runtime transport.

---

# 30. SECTION 12 — LIMITATIONS AND BOUNDARY CONDITIONS

Define conditions that limit what the agent can safely establish or produce.

Examples:

- Required factual input is unavailable.
- Evidence conflicts.
- Evidence remains insufficient.
- A claim cannot be safely strengthened.
- Human recollection is incomplete.
- Structural constraints limit ideal presentation.
- Supporting context is unavailable.
- A product remains materially deficient.

For each condition, define:

- What the limitation is.
- What the role may still safely do.
- What must remain unknown, qualified, or unsupported.
- Whether the limitation should be recorded in the output.

Do not define:

- Routing.
- Escalation.
- Blocking workflow.
- Another agent that must act.
- Next ownership state.

The agent should normally complete the strongest artifact possible within its authority.

---

# 31. LIMITATIONS DO NOT AUTOMATICALLY CREATE REQUESTS

A contract should distinguish between:

    limitation

and:

    authorized request artifact.

A role may only create a request when request generation is itself part of that role's professional authority.

For other roles:

- Preserve the limitation.
- Avoid unsupported claims.
- Record the state where useful.
- Complete the artifact.

This prevents routine ambiguity from creating uncontrolled backward work.

---

# 32. SECTION 13 — COMPLETION CONDITIONS

Define the role's Definition of Done.

Completion Conditions should describe professional state.

Examples:

- Material target requirements have been analyzed.
- Requested factual dimensions have been investigated.
- Strongest current resume has been produced.
- Current resume has been fully evaluated.
- Material limitations are explicit.

Completion must not depend on:

- Another agent accepting the output.
- Another component acting.
- Workflow transition.
- Handoff.
- Routing.
- Queue state.

A valid professional artifact may contain unresolved limitations.

---

# 33. SECTION 14 — PROHIBITED BEHAVIORS

Define durable hard constraints.

Examples:

- Never fabricate professional evidence.
- Never manufacture metrics.
- Never alter employer provenance.
- Never convert transferable evidence into direct evidence without support.
- Never assign corrective ownership.
- Never control runtime workflow.
- Never silently resolve a conflict outside role authority.

Do not use this section for ordinary stylistic preferences.

---

# 34. SECTION 15 — ROLE-SPECIFIC DOCTRINE

Use this section for substantial conceptual guidance unique to the role.

Examples:

## Evidence Analysis Function

- Capability Over Billet.
- Evidence Custody.
- Career-Wide Retrieval.
- Functional Translation.
- Transferability Discipline.

## Human Investigation Function

- Collaborative Interview Posture.
- Memory Development.
- Factual Confirmation.
- Investigation Stopping.
- Evidence Acquisition Versus Classification.

## Resume Writing Function

- Professional Translation.
- Employment Envelope.
- Functional Placement.
- Evidence Before Language.
- Forward Production.

## Resume Evaluation Function

- Two-Pass Evaluation.
- Three Screening Perspectives.
- Visibility Versus Validity.
- Skepticism Without Cynicism.
- Product State Without Corrective Ownership.

## Governance Function

- Governance Versus Execution.
- Kaizen.
- Architectural Conformance.
- Controlled Evolution.

Doctrine must remain durable role behavior rather than task-specific sequence.

---

# 35. SECTION 16 — CONTRACT INTERFACE

Provide a concise summary of the role's artifact interface.

Use:

## Accepts

List artifact or information types the role may consume.

Example:

    Target Job Description
    Job Experience Records
    Evidence Responses

## Produces

List artifact types the role may create.

Example:

    Job Experience Analysis
    Evidence Request
    Process Feedback

For each produced artifact, a brief purpose may be stated.

## Human Interaction

Specify:

    None

or:

    Permitted

or:

    Required

Then define:

- Why human interaction is allowed.
- What kind of information may be sought.
- What authority boundaries apply.

Do not specify communication technology.

Do not include:

- Intended Consumers.
- Destination Agents.
- May Require.
- Routing.
- Corrective Owner.
- Next Step.

The Contract Interface summarizes the role's own observable boundary.

---

# 36. HUMAN INTERACTION

Human interaction is a professional capability, not a transport mechanism.

Contracts may define:

- Whether human interaction is allowed.
- Why it is required.
- What may be asked.
- What confirmation means.
- What the human remains authoritative over.

Contracts must not define:

- Discord.
- Email.
- Chat platform.
- Webhook.
- Notification system.

If direct human interaction is outside the role's authority, state that boundary without naming another runtime agent.

---

# 37. EVIDENCE-CUSTODY CONFORMANCE

All contracts must preserve the system's single authoritative professional evidence model.

Only the evidence-custody function may independently:

- Create authoritative Job Experience Records.
- Modify them.
- Merge them.
- Split them.
- Integrate Evidence Responses.
- Reconcile evidence conflicts.
- Maintain authoritative provenance.
- Determine evidence classification.

Other execution roles may consume professional evidence according to their contracts.

They must not independently mutate authoritative evidence state.

Execution contracts need not name the evidence-custody agent to preserve this rule.

---

# 38. HUMAN-INVESTIGATION CONFORMANCE

Human factual investigation must remain separate from evidence classification.

The human-investigation function may:

- Ask questions.
- Clarify experience.
- Record confirmed facts.
- Record estimates.
- Record uncertainty.
- Record conflicts.
- Produce Evidence Responses.

It must not independently determine:

- Evidence strength.
- Direct versus transferable classification.
- Requirement coverage.
- Job fit.
- Authoritative record consequences.

This separation prevents over-interviewing and preserves global-context analysis.

---

# 39. RESUME-WRITING CONFORMANCE

Resume-writing contracts must preserve:

- Researcher-authorized evidence boundaries.
- Factual provenance.
- Writer presentation authority.
- Functional-role presentation.
- Forward production.
- Traceability.

The resume-writing function must not:

- Acquire new professional evidence.
- Expand evidence authorization.
- Request another runtime component to improve upstream state.
- Stop production because more evidence might theoretically exist.

It produces the strongest current supported resume.

---

# 40. RESUME-EVALUATION CONFORMANCE

Resume-evaluation contracts must preserve independent product judgment.

The evaluation function may determine:

- Requirement visibility.
- Credibility.
- Screening risk.
- Deficiency type.
- Severity.
- Product readiness.

It must not:

- Rewrite the resume.
- Modify evidence.
- Acquire evidence.
- Assign corrective ownership.
- Direct another runtime component.
- Control workflow.

Evaluation artifacts describe product state.

---

# 41. PROCESS FEEDBACK AND KAIZEN

Execution contracts may authorize Process Feedback.

Governance contracts may authorize:

- Feedback analysis.
- Pattern identification.
- Root-cause analysis.
- Draft contract changes.
- Draft task changes.
- Draft schema changes.
- Architecture recommendations.

Governance proposals do not automatically become active architecture.

System Owner approval remains required.

Execution-agent Process Feedback should remain partner-independent and describe the system issue rather than assign a fixer.

---

# 42. FACTUAL INTEGRITY

Every contract must preserve factual integrity above optimization.

No role may improve apparent target fit by:

- Inventing evidence.
- Inventing results.
- Inventing metrics.
- Inventing ownership.
- Inventing scope.
- Inventing systems.
- Inventing qualifications.
- Changing employer provenance.
- Changing employment relationships.
- Converting transferable evidence into direct evidence.
- Converting participation into ownership.

When support is insufficient, the limitation must remain.

---

# 43. PROVENANCE VERSUS PRESENTATION

Contracts should preserve the distinction between:

    Provenance
    = where and when experience occurred.

    Professional capability
    = what the evidence demonstrates.

    Functional classification
    = what recognizable professional function the work represents.

    Presentation
    = how authorized evidence is communicated.

Evidence authority and presentation authority must remain distinct.

---

# 44. ARTIFACT INDEPENDENCE

Contracts should produce artifacts whose meaning does not depend on runtime topology.

Artifacts may contain:

- IDs.
- Versions.
- Related artifact IDs.
- Requirement IDs.
- Evidence IDs.
- Resume IDs.
- Professional-state fields.

They should generally not contain:

- Source agent.
- Destination agent.
- Corrective owner.
- Next agent.
- Queue ownership.
- Workflow status.

The artifact should describe itself.

## Process Feedback Provenance Exception

Production artifacts should not require source-agent identity unless authorship itself is material professional or governance provenance.

**Process Feedback is a deliberate authorship-provenance exception.**

Because governance analysis may depend on which professional function observed a system problem and when it was observed, Process Feedback may identify:

- The feedback owner.
- The owner's professional role.
- The proposal timestamp.

Feedback ownership represents:

- Authorship.
- Observational provenance.
- The professional perspective from which the feedback was produced.

Feedback ownership does **not** represent:

- Corrective ownership.
- Artifact destination.
- Runtime assignment.
- Routing.
- Workflow position.
- Authority to implement the proposed change.
- Authority to determine architectural root cause.
- Authority to approve a governance change.

This exception applies only where authorship is semantically necessary to interpret the artifact.

It does not authorize source-agent identity fields in ordinary production artifacts.

Process Feedback remains a governance-input artifact describing observed system behavior and a proposed interpretation of that behavior. The authoritative determination of architectural root cause remains outside the authority of the feedback-producing function.

---

# 45. CURRENT-SCOPE TEST

Before approving an execution-agent contract, ask:

> Could this role still perform correctly if every other runtime agent were renamed, replaced, or invoked through a completely different topology?

Also ask:

> Could this contract still function if Trello, Discord, Kanban, Python handlers, automated routing, and connectors did not exist?

If not, the contract may contain implementation or partner coupling.

Current V2 contracts should remain usable when:

- Contract is supplied manually.
- Task is supplied manually.
- Relevant artifacts are supplied manually.
- Output artifacts are collected manually.

---

# 46. CONTRACT AUTHORING RULES

When creating or revising an Agent Contract:

1. Conform to `resources/architecture-principles.md`.
2. Follow the required section model.
3. Keep identity separate from procedure.
4. Keep responsibilities separate from authority.
5. Define the role's own authority clearly.
6. Define excluded authority without unnecessary topology awareness.
7. Preserve single authoritative ownership at the system level.
8. Define input authority and precedence.
9. Reference schemas rather than duplicating them.
10. Keep runtime transport out of the contract.
11. Keep partner identity out of execution contracts unless genuinely necessary.
12. Describe output purpose rather than destination.
13. Describe limitations rather than workflow escalation.
14. Preserve forward production.
15. Do not assign corrective ownership.
16. Support current-state reasoning.
17. Support idempotence where appropriate.
18. Put durable doctrine in contracts.
19. Put invocation procedure in task instructions.
20. Put data structures in schemas.
21. Prefer explicit professional state over implied workflow state.
22. Preserve factual integrity.
23. Ensure important context can be represented explicitly.
24. Ensure completion does not require another runtime agent to act.
25. Remove inactive scope rather than preserving speculative capability.

---

# 47. CONTRACT REVIEW CHECKLIST

Before approving a contract, verify:

- [ ] Contract conforms to Architecture Principles.
- [ ] Required section model is followed.
- [ ] Role clearly explains why the function exists.
- [ ] Mission defines a stable professional outcome.
- [ ] Responsibilities are durable.
- [ ] Authority is explicit.
- [ ] Excluded authority is explicit.
- [ ] Required and contextual inputs are identified.
- [ ] Input authority and precedence are defined.
- [ ] Outputs are explicit.
- [ ] Output purposes are clear.
- [ ] No intended-consumer field is required.
- [ ] No corrective ownership is assigned.
- [ ] Operating Principles describe durable doctrine.
- [ ] Authority Boundaries describe decisions rather than topology.
- [ ] Single authoritative ownership is preserved.
- [ ] Evidence acquisition and evidence interpretation remain distinct.
- [ ] Resume presentation cannot expand evidence authority.
- [ ] Product evaluation cannot dispatch corrective work.
- [ ] Decision Rules cover recurring material judgments.
- [ ] Validation requirements test professional output quality.
- [ ] Limitations describe state rather than routing.
- [ ] Completion is independent of workflow.
- [ ] Prohibited Behaviors contain durable hard constraints.
- [ ] Contract Interface uses partner-independent artifact semantics.
- [ ] Shared schemas are referenced rather than duplicated.
- [ ] Task procedure has not leaked into the contract.
- [ ] Runtime implementation assumptions are absent.
- [ ] Human interaction is transport-neutral.
- [ ] Current-state reasoning is supported.
- [ ] Iteration-specific task modes are not required.
- [ ] Idempotence is supported where applicable.
- [ ] Forward production is preserved.
- [ ] Hidden conversational context is not required.
- [ ] The contract remains usable if runtime topology changes.

---

# 48. ARCHITECTURAL NON-CONFORMANCE

A contract is non-conformant when it:

- Grants overlapping authoritative ownership.
- Allows unauthorized mutation of professional evidence.
- Confuses factual acquisition with evidence classification.
- Allows presentation authority to create evidence.
- Allows evaluation authority to dispatch corrective work.
- Assigns corrective ownership in an execution artifact.
- Requires awareness of named partner agents unnecessarily.
- Defines intended consumers as part of execution behavior.
- Encodes workflow state as professional state.
- Authorizes routing or handoffs.
- Authorizes workflow blocking.
- Creates backward requests without explicit professional authority.
- Depends on future implementation technology.
- Embeds shared schemas unnecessarily.
- Requires hidden conversation history.
- Confuses contracts with task procedures.
- Weakens factual integrity for target fit.
- Preserves inactive or speculative scope as though it were implemented.

Correct the problem at the architectural layer that owns it.

Do not compensate for a flawed contract with increasingly complex task instructions.

---

# 49. STANDARD OF COMPLETION

A conforming Agent Contract should allow an agent to answer:

    Who am I?

    Why does my professional function exist?

    What outcome do I own?

    What decisions may I make?

    What information may I trust?

    What artifacts may I consume?

    What artifacts may I produce?

    What does each output represent?

    What decisions are outside my authority?

    How do I make recurring judgments?

    How do I validate my work?

    How do I represent limitations?

    When is my work professionally complete?

The agent should not need to answer:

    Who do I send this to?

    Who fixes this?

    What agent runs next?

    Should I move the workflow backward?

    What queue owns this artifact?

    Which runtime component should I invoke?

If the first set of questions can be answered clearly and the second set is unnecessary, the contract is properly separated from runtime topology.