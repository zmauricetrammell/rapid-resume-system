# RAPID RESUME SYSTEM — ARCHITECTURE PRINCIPLES

**Document Version:** 2.0  
**System:** Rapid Resume System  
**Status:** Active  
**Scope:** Current V2 Architecture

---

# 1. PURPOSE

This document defines the highest-level architectural principles governing the current V2 Rapid Resume System.

These principles govern:

- Agent contracts.
- Agent task instructions.
- Shared schemas.
- Artifact design.
- Agent authority.
- Evidence ownership.
- System governance.
- Future implementation decisions.

All lower-level system artifacts must conform to these principles.

When a contract, task instruction, schema, resource, or implementation conflicts with this document, the conflict must be identified and corrected rather than silently interpreted around.

This document defines the conceptual architecture.

It does not define runtime transport, orchestration, persistence, or connector implementation.

---

# 2. CURRENT SYSTEM SCOPE

Current V2 consists of independent conversational AI reasoning roles operating on explicitly supplied artifacts.

Each invocation may receive:

- An Agent Contract.
- A Task Instruction.
- Relevant current artifacts.
- Relevant feedback.
- Human input when the assigned professional function requires it.

Current V2 may be operated manually by a human.

Current V2 does not require:

- Trello.
- Discord.
- Kanban.
- Automated routing.
- Automated agent invocation.
- Python handlers.
- API connectors.
- Persistent runtime state.
- Automated work ownership.
- Background workers.
- Event-driven orchestration.

Those capabilities may be introduced later.

Current reasoning artifacts must remain valid without them.

---

# 3. CURRENT FUNCTIONAL SCOPE

The active V2 production scope supports:

- Professional evidence management.
- Job-target analysis.
- Human factual evidence investigation.
- Targeted resume generation.
- Independent resume evaluation.
- System governance and continuous improvement.

Cover-letter generation is outside current V2 scope.

A future cover-letter capability may require a separate human-intent and narrative-support architecture and must not be forced into the resume evidence pipeline without deliberate design.

---

# 4. REASONING IS SEPARATE FROM IMPLEMENTATION

The system distinguishes three conceptual layers:

    Reasoning Layer
        ↓
    Runtime / Handler Layer
        ↓
    Connector / Transport Layer

## Reasoning Layer

The reasoning layer contains:

- Agent Contract.
- Task Instruction.
- Supplied artifacts.
- Current context.
- Professional judgment.

It defines what an agent:

- Understands.
- Owns.
- Decides.
- Produces.
- Must not do.

## Runtime / Handler Layer

Future software may manage:

- Agent creation.
- Prompt loading.
- Contract loading.
- Task loading.
- Artifact assembly.
- Invocation.
- Retry behavior.
- Session lifecycle.
- Output collection.
- Iteration decisions.

These are implementation concerns.

## Connector / Transport Layer

Future software may manage:

- Messaging.
- Persistence.
- File storage.
- GitHub.
- Discord.
- Trello.
- Databases.
- Notifications.
- External APIs.
- Artifact retrieval.
- Artifact delivery.

Transport mechanisms must not define professional authority.

---

# 5. TRANSPORT NEUTRALITY

Contracts, tasks, and schemas must remain independent of transport technology.

They may define:

- Required inputs.
- Optional inputs.
- Outputs.
- Artifact purpose.
- Human-interaction requirements.
- Professional constraints.

They must not depend on:

- Cards.
- Queues.
- Lists.
- Inboxes.
- Routing.
- Handoffs.
- Message channels.
- Workflow transitions.
- Connector behavior.

Valid:

    Produce an Evidence Request describing a factual uncertainty.

Invalid:

    Move the card to the Interviewer queue.

Valid:

    Ask the human one primary question at a time.

Invalid:

    Send the question through Discord.

---

# 6. PARTNER-INDEPENDENT RUNTIME AGENTS

Execution agents are partner-independent.

A runtime agent must not require awareness of:

- Which other runtime agents exist.
- Which agent produced an input artifact.
- Which agent will consume an output artifact.
- Which agent should correct a deficiency.
- Which component should act next.
- Runtime topology.

An execution agent reasons from:

    its own contract
    + its task
    + supplied artifacts
    + its own authority boundaries

and produces a self-contained artifact.

The artifact must remain useful regardless of which authorized human or software component consumes it.

---

# 7. AUTHORITY WITHOUT TOPOLOGY AWARENESS

The system architecture must define authoritative ownership.

Individual execution agents need only understand:

- What they own.
- What they may decide.
- What they may not decide.
- What information is authoritative for their work.
- When their professional task is complete.

They do not need to know which named agent owns every excluded decision.

For example, an execution contract may state:

    Do not modify authoritative professional evidence.

It need not state:

    Researcher owns this decision.

System-level documentation may describe ownership relationships.

Runtime execution instructions should minimize knowledge of the system topology.

---

# 8. ROLE SPECIALIZATION

Each professional function should have a clear authority boundary.

Current system-level ownership is:

    Professional evidence and job analysis
    → Researcher function

    Human factual evidence acquisition
    → Interviewer function

    Resume presentation
    → Writer function

    Resume product judgment
    → Evaluator function

    System governance
    → Supervisor function

    Architecture adoption
    → System Owner

This ownership map exists for system governance.

It does not imply that runtime agents must know or communicate with one another directly.

---

# 9. SINGLE AUTHORITATIVE OWNER

Every mutable information domain or material professional judgment should have one authoritative owner.

Avoid architectures where:

- Multiple agents independently modify the same state.
- Multiple agents believe they own the same judgment.
- No component owns a required decision.
- Runtime agents negotiate ownership during execution.

Single ownership reduces:

- Conflict.
- Reconciliation overhead.
- Behavioral loops.
- Ambiguous state.
- Hidden coupling.

---

# 10. AUTHORITATIVE PROFESSIONAL EVIDENCE

The professional evidence model has one authoritative custodian.

The evidence-custody function owns:

- Evidence retrieval.
- Evidence interpretation.
- Evidence integration.
- Evidence reconciliation.
- Job Experience Record creation.
- Job Experience Record modification.
- Record merging.
- Record splitting.
- Provenance.
- Evidence conflicts.
- Functional-role classification.
- Transferability.
- Requirement-to-evidence mapping.
- Job-fit analysis.
- Evidence-gap determination.
- Evidence Request generation.

No other runtime function may independently mutate authoritative professional evidence.

---

# 11. HUMAN EVIDENCE ACQUISITION

Human evidence acquisition is distinct from evidence interpretation.

The factual-investigation function owns:

- Collaborative questioning.
- Memory prompting.
- Responsibility clarification.
- Ownership clarification.
- Scope clarification.
- Result clarification.
- Attribution clarification.
- Human confirmation.
- Evidence Response generation.

Its transformation is:

    Factual Investigation Specification
            ↓
    Human Conversation
            ↓
    Supportable Facts
            ↓
    Evidence Response

It does not determine:

- Evidence strength.
- Direct versus transferable classification.
- Requirement coverage.
- Job fit.
- Authoritative record consequences.

The factual acquisition artifact records what can be established.

Interpretation occurs only after integration with the wider evidence model.

---

# 12. RESUME PRESENTATION AUTHORITY

The resume-writing function owns presentation of authorized professional evidence.

It owns:

- Resume composition.
- Content placement.
- Supported functional-role presentation.
- Bullet construction.
- Narrative structure.
- Concision.
- Keyword placement.
- Formatting within approved constraints.
- Target professional identity.
- Writer Content Manifest maintenance.

It may:

- Select among authorized evidence.
- Omit authorized evidence for relevance or space.
- Reorganize authorized evidence for recruiter comprehension.
- Translate supported terminology into civilian-recognizable language.

It may not:

- Expand the evidence boundary.
- Invent professional evidence.
- Reconcile factual conflicts.
- Reclassify evidence beyond authorization.
- Acquire new professional evidence.
- Demand upstream improvement.

---

# 13. RESUME PRODUCT-JUDGMENT AUTHORITY

The resume-evaluation function owns independent judgment of the current resume product.

It may judge:

- Requirement visibility.
- ATS explicitness.
- Recruiter comprehension.
- Hiring-manager evidence strength.
- Claim credibility.
- Screening risk.
- Requirement coverage.
- Professional positioning.
- Seniority alignment.
- Submission readiness.
- Material product deficiencies.

It evaluates:

> What does the current resume actually demonstrate to a reasonable external reviewer?

It does not:

- Modify evidence.
- Rewrite the resume.
- Acquire evidence.
- Assign corrective work.
- Identify which runtime component must act next.

Its output describes product state.

---

# 14. GOVERNANCE AUTHORITY

The governance function maintains the architecture.

It may:

- Review contracts.
- Review tasks.
- Review schemas.
- Identify conflicts.
- Analyze recurring Process Feedback.
- Draft proposed improvements.
- Draft revised contracts.
- Draft revised tasks.
- Draft revised schemas.
- Recommend architecture changes.
- Recommend version changes.

Governance proposes.

The System Owner approves adoption into the active system.

---

# 15. PROFESSIONAL STATE OVER WORKFLOW STATE

Execution agents describe professional state.

They do not control workflow state.

Examples of professional state:

- Evidence is insufficient to establish direct ownership.
- The resume does not visibly demonstrate a critical requirement.
- A factual conflict remains unresolved.
- Structural constraints reduce available presentation space.
- A claim is unsupported.
- Current evidence supports only a qualified statement.

Examples of workflow state that execution agents must not own:

- Block the workflow.
- Send backward.
- Route to another agent.
- Move to another queue.
- Retry another component.
- Require another agent to act.
- Stop progression.

Infrastructure may later use professional state to make workflow decisions.

That decision belongs outside execution-agent reasoning.

---

# 16. FORWARD PRODUCTION

Execution agents should complete the strongest professional artifact possible from the current supplied state.

An agent should not interrupt production merely because:

- Better evidence might exist.
- More detail might improve the artifact.
- Another component could theoretically improve an input.
- The current state is imperfect.
- The candidate is not a perfect match.

Instead:

    Preserve factual integrity
            ↓
    Use strongest available authorized state
            ↓
    Record material limitations
            ↓
    Produce the artifact
            ↓
    Complete the task

Imperfection is not authority to create backward work.

---

# 17. ITERATION THROUGH RICHER STATE

System improvement occurs through repeated execution against richer current state.

Conceptually:

    Produce
        ↓
    Evaluate
        ↓
    New information exists
        ↓
    Invoke relevant task again with richer artifacts
        ↓
    Produce stronger current state

The system should not model iteration as runtime agents sending work backward.

A previous output becomes another artifact in the next invocation.

A failed or insufficient evaluation becomes new information.

The same task runs again.

---

# 18. DOWNSTREAM JUDGMENTS BECOME ARTIFACT STATE

A product judgment made within valid authority should be preserved as explicit artifact state.

For example:

    Current resume does not sufficiently demonstrate vendor ownership.

That judgment may later influence another invocation.

The judgment does not need to:

- Name another agent.
- Assign corrective ownership.
- Demand action.
- Specify routing.

The artifact preserves the observation.

Future reasoning may incorporate it.

---

# 19. NO CORRECTIVE OWNERSHIP IN EXECUTION ARTIFACTS

Execution artifacts should describe deficiencies, not assign fixers.

Prefer:

    Deficiency Type:
    Evidence Visibility

    Observation:
    Direct ownership is not sufficiently visible.

    Successful Future State:
    Product clearly communicates the strongest supportable ownership.

Avoid:

    Corrective Owner:
    Writer

or:

    Send to Researcher.

This keeps artifacts partner-independent.

---

# 20. ARTIFACT PURPOSE OVER RECIPIENT

Artifacts should define:

- What they represent.
- What information they contain.
- What professional state they establish.

They should not require fields such as:

- Intended consumer.
- Destination agent.
- Source agent.
- Routing target.
- Next owner.

For example:

    Evidence Request

    Purpose:
    Define a factual question requiring human investigation.

rather than:

    Intended consumer:
    Interviewer.

Artifact semantics should survive changes in runtime topology.

---

# 21. STRUCTURED ARTIFACTS ARE THE INTERFACE

Important system information should be captured in explicit artifacts.

Current artifact families include:

- Job Experience Record.
- Job Experience Analysis.
- Evidence Request.
- Evidence Response.
- Targeted Resume.
- Writer Content Manifest.
- Resume Evaluation.
- Process Feedback.

An artifact must contain sufficient information for an authorized consumer to use it without access to another agent's hidden reasoning.

The artifact is the interface.

The conversation is not.

---

# 22. MINIMIZE HIDDEN CONTEXT

Do not rely on information that exists only in another conversation.

Material:

- Facts.
- Decisions.
- Deficiencies.
- Qualifications.
- Uncertainty.
- Evidence.
- Feedback.
- Output state.

should be represented explicitly.

Prefer:

    explicit artifact

over:

    assumed shared memory

This supports:

- Reproducibility.
- Auditability.
- Human inspection.
- Model replacement.
- Agent replacement.
- Future automation.
- Independent testing.

---

# 23. CONTRACTS DEFINE DURABLE BEHAVIOR

An Agent Contract defines persistent role behavior.

It answers:

- What is this role?
- What is its mission?
- What does it own?
- What authority does it have?
- What inputs may it trust?
- What outputs may it produce?
- What must it not do?
- What is outside its authority?
- When is its work complete?

Contracts describe professional reasoning.

They do not describe runtime topology.

---

# 24. TASK INSTRUCTIONS DEFINE KINDS OF WORK

A Task Instruction defines one repeatable operation.

It answers:

- What work is being performed?
- What inputs are considered?
- What process is followed?
- What output is produced?
- What validation occurs?
- What completion means?

A task must represent a genuine kind of work.

Workflow position alone does not justify a new task.

---

# 25. TASK IDENTITY IS NOT ITERATION STATE

Avoid separate tasks such as:

- Generate.
- Regenerate.
- Revise.
- Recheck.
- Reevaluate.

when the underlying professional operation is unchanged.

Prefer:

    generate_analysis

meaning:

> Produce the best current analysis from all current supplied artifacts.

Prefer:

    generate_resume

meaning:

> Produce the best current resume from all current supplied artifacts.

Prefer:

    evaluate_resume

meaning:

> Evaluate the current resume against the current target and supplied context.

Iteration changes inputs.

It does not necessarily change the task.

---

# 26. IMPLIED SUB-OPERATIONS DO NOT REQUIRE NEW TASKS

A professional task may include subordinate operations inherently required to perform it.

For example, maintaining authoritative evidence may require:

- Integrating new Evidence Responses.
- Updating records.
- Reconciling facts.

Those actions need not become separate tasks when there is no meaningful use case for performing them independently.

Create a new task only when the professional operation is genuinely distinct and independently useful.

---

# 27. IDEMPOTENCE

Tasks should be idempotent when practical.

Given materially identical:

- Inputs.
- Evidence.
- Feedback.
- Constraints.

repeated execution should converge on materially stable decisions.

Idempotence does not require identical wording.

It requires stability in material professional judgment.

Avoid:

- Rewriting for novelty.
- New criticism without new basis.
- Arbitrary reprioritization.
- Different classifications without changed evidence.

New information may justify change.

Unchanged information should generally produce convergence.

---

# 28. CURRENT-STATE REASONING

Agents evaluate the complete current artifact set.

Prior outputs are historical context.

They are not automatically immutable conclusions.

A prior analysis may be reconsidered when:

- New evidence exists.
- New feedback exists.
- A prior interpretation proves insufficient.
- Authoritative evidence changes.

A prior resume may be reconsidered when:

- Analysis changes.
- Evaluation changes.
- Constraints change.

The governing question is:

> What is the strongest correct state now?

---

# 29. PRESERVE STABLE INFORMATION

Current-state reasoning does not mean rewriting everything.

Agents should preserve material that remains optimal.

The desired behavior is:

    Reconsider what matters.

    Change only what materially benefits from change.

The system seeks convergence rather than novelty.

---

# 30. EVIDENCE REQUESTS REPRESENT FACTUAL NEED

An Evidence Request represents a factual investigation need.

It should describe:

- What is known.
- What remains unknown.
- Why the missing information matters.
- What facts must not be assumed.
- What factual dimensions require investigation.
- What analytical limitation currently exists.

It should not describe:

- Routing.
- Runtime ownership.
- Workflow blocking.
- Destination agent.
- Required sequence.

Evidence Requests should only be produced after reasonable existing evidence retrieval has been exhausted.

---

# 31. EVIDENCE RESPONSES REPRESENT FACTS

An Evidence Response represents the factual result of human investigation.

It may contain:

- Confirmed facts.
- Qualified facts.
- Estimates.
- Unsupported possibilities.
- Remaining uncertainty.
- Conflicting facts.
- Addressed requested dimensions.
- Unresolved requested dimensions.

It must not independently determine:

- Evidence strength.
- Direct versus transferable classification.
- Requirement coverage.
- Job fit.
- Authoritative record consequences.

Those judgments require integration with the broader evidence model.

---

# 32. EVIDENCE CLASSIFICATION REQUIRES GLOBAL CONTEXT

Evidence should not be classified solely from an isolated interview response.

Classification may require:

- Career-wide context.
- Other evidence.
- Provenance.
- Target requirements.
- Existing records.
- Contradictory information.
- Related professional episodes.

Therefore:

> Evidence acquisition and evidence classification remain separate operations.

This prevents factual investigation from expanding unnecessarily merely to create a self-contained analytical conclusion.

---

# 33. FACTUAL INTEGRITY OVERRIDES OPTIMIZATION

No optimization objective may override factual integrity.

Never improve apparent fit by:

- Inventing experience.
- Inventing metrics.
- Inventing responsibility.
- Inventing ownership.
- Inventing scope.
- Inventing systems.
- Inventing results.
- Inventing certifications.
- Inventing education.
- Changing employer provenance.
- Changing employment history.
- Converting contribution into ownership.
- Converting transferable evidence into direct evidence.
- Misstating attribution.

When evidence is insufficient, preserve the limitation.

---

# 34. PROVENANCE AND PRESENTATION ARE DISTINCT

Maintain the distinction between:

    Provenance
    = where, when, and under what employment relationship experience occurred.

    Professional capability
    = what the experience demonstrates.

    Functional classification
    = what recognizable professional function the work represents.

    Presentation
    = how authorized evidence is communicated.

Professional translation is allowed.

Historical fabrication is not.

---

# 35. DIRECT AND TRANSFERABLE EVIDENCE REMAIN DISTINCT

The system should recognize transferable professional capability.

Terminology, military context, internal titles, and unusual organizational structures should not create artificial gaps.

However:

    Similar tool ≠ direct tool experience

    Related industry ≠ direct industry experience

    Supporting work ≠ ownership

    Knowledge ≠ certification

    Adjacent capability ≠ identical capability

Transferability should reduce unnecessary translation burden without inflating evidence.

---

# 36. LIMITATIONS ARE VALID STATE

An artifact does not need to be perfect to be complete.

Valid professional state may include:

- Unknown information.
- Weak evidence.
- Qualified evidence.
- Genuine gaps.
- Structural constraints.
- Partial requirement coverage.
- Product deficiencies.
- Factual conflicts.

Agents should represent limitations accurately rather than creating requests merely because limitations exist.

---

# 37. PRODUCT READINESS IS NOT WORKFLOW AUTHORITY

The evaluation function may judge:

- Ready to submit.
- Not ready to submit.
- Weak fit.

This is a professional product judgment.

It does not mean:

- Stop workflow.
- Block execution.
- Route backward.
- Require another agent to act.

Product readiness and runtime workflow state must remain distinct.

---

# 38. PROCESS FEEDBACK IS SEPARATE FROM PRODUCTION OUTPUT

Execution roles may identify recurring system problems while performing normal work.

Examples include:

- Contract ambiguity.
- Schema weakness.
- Repeated missing artifact fields.
- Repeated task friction.
- Recurring authority confusion.
- Repeated interface failures.

When materially useful, the agent may additionally produce Process Feedback.

Process Feedback describes system-level friction.

It does not:

- Modify architecture.
- Assign corrective ownership.
- Control runtime behavior.

---

# 39. KAIZEN IS GOVERNED CHANGE

The governance function may analyze Process Feedback and draft improvements.

The continuous-improvement model is:

    Observe
        ↓
    Identify pattern
        ↓
    Analyze root cause
        ↓
    Identify owning architectural layer
        ↓
    Draft improvement
        ↓
    Validate architecture
        ↓
    System Owner review
        ↓
    Approve / reject / modify
        ↓
    Adopt new standard

Governance may autonomously diagnose and draft.

The System Owner retains adoption authority.

---

# 40. SCHEMAS DEFINE DATA, NOT BEHAVIOR

Schemas define structured artifact interfaces.

A schema answers:

- What fields exist?
- Which fields are required?
- What types are permitted?
- What identifiers connect related artifacts?
- What values are valid?

Schemas should not define:

- Runtime routing.
- Destination agents.
- Corrective owners.
- Workflow transitions.
- Agent behavior.
- Task procedure.

Schemas describe professional state.

---

# 41. ARTIFACT IDENTITY IS VALID; RUNTIME DESTINATION IS NOT

Artifacts may contain stable identifiers such as:

- Artifact ID.
- Version.
- Superseded version.
- Related artifact IDs.
- Requirement IDs.
- Evidence IDs.
- Resume IDs.

These support:

- Traceability.
- Correlation.
- Versioning.
- Auditability.

They should not require:

- Source-agent IDs.
- Destination-agent IDs.
- Next-agent fields.
- Queue ownership.
- Workflow status.

Artifact identity and runtime topology are separate concerns.

---

# 42. PREFER THE SIMPLEST COHERENT INTERFACE

Do not create a new:

- Artifact.
- Task.
- Role.
- State.
- Classification.

unless it represents genuinely distinct information or work.

Prefer:

    one reusable task

over:

    iteration-specific tasks

Prefer:

    one Evidence Request artifact

over:

    agent-specific request types

Prefer:

    limitations recorded in an existing manifest

over:

    separate request artifacts with no independent purpose

Prefer:

    one authoritative evidence owner

over:

    competing evidence copies

Complexity must solve a real problem.

---

# 43. HUMAN INTERACTION IS A CAPABILITY, NOT TRANSPORT

Some professional functions require direct human interaction.

Contracts may define:

- Why human interaction is required.
- What information may be requested.
- What confirmation is needed.
- What boundaries apply.

They must not specify:

- Discord.
- Email.
- Chat platform.
- Webhook.
- Messaging transport.

The professional interaction model must survive changes in communication technology.

---

# 44. FUTURE IMPLEMENTATION MUST PRESERVE CONCEPTUAL BOUNDARIES

Future software may introduce:

- Python handlers.
- Persistent agents.
- Databases.
- Message buses.
- Queues.
- GitHub.
- Discord.
- Trello.
- Automated routing.
- Background jobs.
- Retry behavior.

Those mechanisms implement the architecture.

They must not redefine:

- Evidence authority.
- Professional judgment.
- Artifact meaning.
- Human approval boundaries.
- Task semantics.
- Role specialization.

Runtime code may decide which component receives an artifact.

The artifact-producing agent does not need to know that decision.

---

# 45. CURRENT V2 TASK MODEL

The active V2 production task set is:

    Researcher Function
    ├── generate_analysis
    └── request_evidence

    Human Evidence Acquisition Function
    └── investigate_evidence_request

    Resume Writing Function
    └── generate_resume

    Resume Evaluation Function
    └── evaluate_resume

System governance work is governed separately.

Cover-letter generation is not part of the current active task model.

---

# 46. CURRENT V2 ARTIFACT MODEL

Primary artifact families currently include:

    Professional Evidence
    ├── Job Experience Record
    └── related atomic evidence

    Job Analysis
    └── Job Experience Analysis

    Human Investigation
    ├── Evidence Request
    └── Evidence Response

    Resume Production
    ├── Targeted Resume
    └── Writer Content Manifest

    Resume Evaluation
    └── Resume Evaluation

    Governance
    └── Process Feedback

Schemas should represent these artifacts according to their professional meaning rather than runtime relationships.

---

# 47. ARCHITECTURAL CONFORMANCE TEST

When reviewing a contract, task, schema, or implementation, ask:

## Authority

- Is the role's own authority explicit?
- Are excluded decisions clear?
- Is authoritative mutable state owned exactly once?

## Partner Independence

- Does the runtime agent need to know another runtime agent exists?
- Does the artifact name a destination or corrective owner unnecessarily?
- Could the task still operate if the system topology changed?

## Professional State

- Does the artifact describe what is true?
- Or does it attempt to control what happens next?

## Forward Production

- Does the agent produce the strongest current artifact?
- Or does ambiguity unnecessarily create backward requests?

## Evidence

- Is factual acquisition separate from evidence interpretation?
- Is classification performed with sufficient global context?
- Is authoritative evidence protected?

## Iteration

- Does new information become richer current state?
- Or has workflow iteration been encoded as separate task identity?

## Artifact Design

- Is the artifact self-contained?
- Does it depend on hidden conversation history?
- Does it describe purpose rather than recipient?

## Scope

- Does the reasoning artifact assume:
  - Trello?
  - Discord?
  - Kanban?
  - Routing?
  - Python handlers?
  - Connectors?
  - Automated workflow?

If yes, determine whether implementation concerns have leaked into the reasoning layer.

---

# 48. GOVERNING PRINCIPLES

The Rapid Resume System follows these governing rules:

1. **Professional authority is explicit.**
2. **Authoritative mutable state has one owner.**
3. **Runtime agents are partner-independent.**
4. **Agents know their boundaries, not the runtime topology.**
5. **Artifacts describe professional state, not workflow state.**
6. **Artifacts describe purpose, not destination.**
7. **Agents produce forward from the current state.**
8. **Imperfection does not automatically create backward work.**
9. **Iteration occurs through richer current artifacts.**
10. **Evidence acquisition and evidence interpretation remain separate.**
11. **Professional evidence remains authoritative and traceable.**
12. **Presentation cannot create truth.**
13. **Evaluation judges the product without dispatching corrective work.**
14. **Tasks represent kinds of work, not workflow iterations.**
15. **Tasks should converge under unchanged inputs.**
16. **Explicit artifacts replace hidden shared memory.**
17. **Schemas describe structured state rather than behavior or routing.**
18. **Governance proposes; the System Owner adopts.**
19. **Current reasoning must remain independent of future implementation.**
20. **Complexity must justify itself.**

---

# 49. GOVERNING MODEL

At its core, the Rapid Resume System is:

> A set of specialized, partner-independent reasoning functions operating within explicit authority boundaries, consuming self-contained artifacts, producing self-contained professional state, and converging through repeated execution against increasingly complete information.

Current V2 should implement that conceptual model as simply as possible.

Future automation should make the system easier to operate.

It should not be necessary to explain how the reasoning system works.