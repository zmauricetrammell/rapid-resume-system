# RESEARCHER TASK INSTRUCTION — REQUEST EVIDENCE

**Task Version:** 2.0  
**Task ID:** request_evidence  
**Agent:** Researcher  
**System:** Rapid Resume System

---

# 1. TASK

Generate an Evidence Request when the current authoritative professional evidence is insufficient to resolve a material factual question and additional human evidence may plausibly clarify or resolve it.

This task converts an identified evidence deficiency into a focused factual investigation specification for the Interviewer.

The Researcher determines:

- What is currently known.
- What remains unknown.
- Why the missing information matters.
- Which professional context is most promising.
- What facts must not be assumed.
- What factual dimensions require clarification.
- What outcomes would constitute full, partial, transferable, or negative resolution.

The Researcher does not determine how the human interview must be conducted.

The Interviewer owns the questioning strategy.

The task is idempotent in intent:

> Given materially identical evidence, uncertainty, requirement context, and prior request history, repeated execution should converge on the same open Evidence Request rather than generating unnecessary duplicates.

---

# 2. OBJECTIVE

Produce a focused Evidence Request that allows the Interviewer to investigate a material factual question without independently repeating the Researcher's evidence analysis.

The request must establish:

1. What requirement or factual issue is affected.
2. What the authoritative evidence already establishes.
3. What remains unresolved.
4. Why the unresolved information matters.
5. Which existing professional experiences are the best starting points for investigation.
6. Which facts must not be assumed.
7. Which factual dimensions should be explored.
8. What would constitute full resolution.
9. What would constitute partial resolution.
10. What would constitute transferable resolution when applicable.
11. What would confirm that the requested experience is absent.
12. What analytical or claim limitation remains while the question is unresolved.

The Evidence Request defines the factual problem.

The Interviewer determines how to investigate it conversationally.

---

# 3. INPUT MODEL

The Researcher must review all relevant current artifacts before requesting new human evidence.

## Minimum Required Inputs

- Identified material evidence deficiency or factual uncertainty.
- Current authoritative professional evidence relevant to that deficiency.

## Contextual Inputs

When available, also consider:

- Target Job Description.
- Current Job Experience Analysis.
- Previous Job Experience Analyses.
- Relevant Job Experience Records.
- Atomic Experience Points.
- Previous Evidence Requests.
- Previous Evidence Responses.
- Writer feedback.
- Evaluator feedback.
- Writer Content Manifest.
- Current targeted resume.
- Employment provenance records.
- Confirmed corrections.
- Supporting source materials.
- Other relevant artifacts supplied with the current invocation.

Before generating an Evidence Request, the Researcher must determine that reasonable retrieval and analysis of existing authoritative evidence has already occurred.

---

# 4. REQUEST THRESHOLD

Generate an Evidence Request only when all of the following are true:

- The factual issue is materially relevant.
- Current authoritative evidence is insufficient.
- Reasonable career-wide retrieval has already been performed.
- Relevant terminology variants have been considered.
- Adjacent responsibilities have been considered.
- Direct and transferable evidence have been evaluated.
- The missing information is factual rather than purely presentational.
- Additional human investigation could plausibly resolve or materially clarify the issue.

Do not generate an Evidence Request for:

- Resume formatting problems.
- Resume wording problems.
- Content-ordering problems.
- Keyword placement problems.
- Evidence that already exists but merely needs stronger selection.
- Evidence that already exists but merely needs clearer presentation.
- Low-value details unlikely to affect material analysis.
- Questions already resolved by a prior Evidence Response.
- Confirmed gaps unless new information creates a genuinely different factual issue.

The Researcher must exhaust reasonable existing evidence before asking the human to supply more.

---

# 5. PROCESS

## Phase 1 — Identify the Factual Issue

Identify the specific requirement, evidence deficiency, conflict, or uncertainty requiring investigation.

Preserve as applicable:

- Requirement ID.
- Original job-description language.
- Normalized requirement.
- Requirement priority.
- Related evidence IDs.
- Related Job Experience Record IDs.
- Related analysis IDs.
- Relevant downstream deficiency IDs.

Determine why the unresolved fact matters analytically.

Do not reduce every Evidence Request to a target-job gap.

An Evidence Request may also exist because:

- Existing records conflict.
- Ownership is unclear.
- Scope is unclear.
- Attribution is unclear.
- A result is insufficiently established.
- Direct versus transferable experience cannot yet be distinguished.
- Evidence may be incomplete.

---

## Phase 2 — Review Existing Evidence

Identify all current authoritative evidence relevant to the issue.

Include as applicable:

- Direct evidence.
- Transferable evidence.
- Adjacent evidence.
- Relevant responsibilities.
- Relevant actions.
- Relevant ownership.
- Relevant scope.
- Relevant tools or systems.
- Relevant results.
- Existing functional-role classifications.
- Previous Evidence Requests.
- Previous Evidence Responses.

Summarize what the authoritative evidence already establishes.

Do not ask the Interviewer to rediscover information the system already knows.

---

## Phase 3 — Define the Missing Evidence

Identify precisely what remains unknown or insufficient.

Possible dimensions include:

- Responsibility.
- Personal action.
- Ownership.
- Decision authority.
- Leadership role.
- Team contribution.
- Scope.
- Organizational scope.
- User or customer scope.
- Geographic scope.
- Budget.
- Systems affected.
- Tools used.
- Complexity.
- Duration.
- Frequency.
- Proficiency.
- Result.
- Before-and-after condition.
- Attribution.
- Business significance.
- Operational significance.
- Customer significance.
- Direct versus transferable relationship.
- Conflicting values or definitions.

Avoid vague statements such as:

    Need more detail.

    Need stronger evidence.

    Need more leadership evidence.

    Need better metrics.

State exactly what factual information is unresolved.

---

## Phase 4 — Identify Promising Professional Context

Identify the strongest existing professional experiences that may contain the missing evidence.

For each promising context, provide:

- Experience or record ID.
- Relevant role or employment context.
- What is already known.
- Why this experience may contain the missing evidence.
- Which factual dimensions may be worth exploring.

The Interviewer should receive enough context to begin intelligently.

Do not imply that adjacent experience proves the missing fact.

---

## Phase 5 — Define Facts That Must Not Be Assumed

Explicitly identify facts that must not be inferred during the investigation.

Examples:

- Coordination does not automatically establish ownership.
- Leadership does not automatically establish direct reports.
- Tool familiarity does not automatically establish production administration.
- Team results do not automatically establish individual attribution.
- Similar systems do not automatically establish direct tool experience.
- Military authority does not automatically establish a specific civilian management responsibility.
- A result is not automatically measured merely because an outcome occurred.
- Transferable evidence does not automatically become direct evidence.
- Current recollection does not automatically supersede an older confirmed record.
- Participation does not automatically establish decision authority.

These constraints protect factual integrity during human evidence acquisition.

---

## Phase 6 — Define Investigative Objectives

Describe the factual questions the investigation needs to answer.

Do not prescribe a rigid interview script.

Prefer factual objectives such as:

    Determine whether the job hunter personally monitored vendor performance.

    Determine whether the job hunter controlled escalation or corrective action.

    Determine whether the job hunter had renewal or contract authority.

    Determine the approximate number of vendors involved.

    Determine whether service expectations were formally measured.

Avoid prescribing exact questions unless a very specific clarification is necessary.

The Researcher defines:

> What facts must be established?

The Interviewer determines:

> How should those facts be explored with the human?

---

# 6. RESOLUTION CRITERIA

Every Evidence Request must define clear factual resolution conditions.

## Full Resolution

Define what evidence would fully resolve the issue.

Example:

    Full resolution requires confirmed evidence that the job hunter
    personally owned or materially led vendor-performance management,
    including responsibility for service expectations, escalation,
    corrective action, or performance review.

Full resolution should describe the factual state required.

It should not dictate the answer.

---

## Partial Resolution

Define what evidence would improve support while leaving a meaningful limitation.

Example:

    Partial resolution exists if the job hunter coordinated vendor
    performance or escalations but did not own SLA definition,
    enforcement, or contracting decisions.

State the remaining limitation.

---

## Transferable Resolution

When relevant, define what would establish related professional capability without direct experience.

Example:

    Transferable resolution exists if the job hunter managed internal
    service-performance targets using substantially similar governance
    and escalation practices but did not directly manage external vendors.

Do not collapse transferable resolution into full direct resolution.

---

## Confirmed Gap

Define what would establish that the requested experience is not present.

Example:

    Confirmed gap exists if the job hunter confirms that they did not
    own, lead, materially support, or perform comparable vendor-performance
    responsibilities in any relevant role.

The answer:

    I do not have that experience.

is a valid successful factual resolution.

---

# 7. ANALYTICAL IMPACT

The Researcher must describe why the unresolved evidence matters without defining workflow state.

Do not use concepts such as:

- Blocking workflow.
- Blocking progression.
- Stopping the card.
- Preventing handoff.

Instead describe professional state.

Possible fields or concepts include:

## Requirement Materiality

Examples:

- Critical.
- High.
- Moderate.
- Low.

## Analytical Impact

Examples:

- Prevents confident direct-evidence classification.
- Prevents determination of ownership.
- Prevents reliable scope assessment.
- Prevents safe attribution of result.
- Limits fit assessment to partial support.
- Prevents use of a specific claim.
- Does not materially affect core fit but could improve differentiation.

## Claim Constraint

When useful, state what must remain unclaimed while the issue is unresolved.

Example:

    Do not claim direct vendor-performance ownership until this issue is resolved.

## Current Supported Position

State what can still safely be concluded.

Example:

    Current evidence supports vendor coordination but not direct SLA ownership.

Agents describe professional and analytical state.

They do not control workflow state.

---

# 8. OUTPUT

Produce an Evidence Request conforming to the authoritative schema under:

    /schemas/evidence-request.yaml

The Evidence Request should include, at minimum:

- Request ID.
- Related Target Job ID when applicable.
- Related requirement IDs when applicable.
- Related evidence IDs.
- Related Job Experience Record IDs.
- Reason for request.
- Current evidence summary.
- Missing evidence dimensions.
- Promising professional context.
- Facts that must not be assumed.
- Investigative objectives.
- Full-resolution criteria.
- Partial-resolution criteria.
- Transferable-resolution criteria when applicable.
- Confirmed-gap criteria.
- Requirement materiality.
- Analytical impact.
- Claim constraints when applicable.
- Current supported position.
- Originating artifact references.
- Related prior Evidence Request IDs when applicable.

The Evidence Request should contain enough analytical context that the Interviewer does not need to repeat the Researcher's career-wide evidence search.

---

# 9. OUTPUT INTERFACE

## Primary Output

### Evidence Request

Intended consumer:

    Interviewer

The Evidence Request defines the factual investigation required.

## Expected Corresponding Artifact

The logical response artifact is:

    Evidence Response

Produced by:

    Interviewer

The Researcher later determines how any Evidence Response affects authoritative professional evidence.

The task does not define transport, routing, workflow ownership, or communication technology.

---

# 10. MULTIPLE EVIDENCE REQUESTS

A single Researcher analysis may identify more than one factual deficiency.

Use one Evidence Request for one coherent factual investigation.

Closely related missing dimensions concerning the same professional episode should normally remain together.

For example:

    ownership
    + scope
    + result
    + attribution

may belong in one Evidence Request when they concern the same professional episode.

Generate separate Evidence Requests when investigations are materially independent.

Examples:

- Different professional episodes.
- Different unrelated capabilities.
- Different factual conflicts.
- Different source contexts requiring separate human recall.
- Different requirements whose investigation would not meaningfully overlap.

Prefer the smallest set of coherent investigations.

Do not fragment one professional episode into unnecessary micro-requests.

---

# 11. DUPLICATE AND REPEAT REQUEST CONTROL

Before generating a new Evidence Request:

1. Check whether the same factual issue has previously generated a request.
2. Review the prior request.
3. Review any corresponding Evidence Response.
4. Determine whether the factual question remains unresolved.
5. Determine whether the current question is materially different.
6. Reuse or update the existing request when appropriate.
7. Create a new request only when a genuinely distinct factual investigation is required.

Given materially identical:

- Evidence deficiency.
- Existing authoritative evidence.
- Requirement context.
- Prior request history.

repeated execution should not generate duplicate Evidence Requests.

A new request may be appropriate when:

- New evidence changes the factual question.
- A prior partial resolution exposes a narrower unresolved issue.
- A downstream deficiency identifies a different missing dimension.
- New conflicting evidence appears.
- The previous request investigated a materially different context.

Preserve traceability between related requests.

---

# 12. EVIDENCE REQUESTS FOR CONFLICT RESOLUTION

An Evidence Request may be generated to resolve conflicting authoritative evidence.

In that case, clearly identify:

- Existing value or interpretation A.
- Existing value or interpretation B.
- Source or provenance of each.
- Why they appear inconsistent.
- Whether both could plausibly be true under different scopes or definitions.
- What factual clarification is required.

For example:

    Existing record:
    Managed 10 vendors.

    New confirmed statement:
    Managed 12 vendors.

    Possible explanation:
    10 may refer to active service vendors while 12 refers to total vendors.

    Investigative objective:
    Determine what each count represented.

Do not ask the Interviewer to decide which value should become authoritative.

The Interviewer acquires clarification.

The Researcher performs reconciliation.

---

# 13. EVIDENCE REQUESTS FOR DIRECT VERSUS TRANSFERABLE EXPERIENCE

When the unresolved issue concerns direct versus transferable experience:

Clearly define:

- What direct evidence would require.
- What related capability is already supported.
- What important difference remains unresolved.
- What facts would establish direct experience.
- What facts would establish transferable-only experience.
- What facts would confirm no meaningful support.

Do not frame transferable evidence as a failed direct-experience answer.

The purpose is accurate classification.

---

# 14. PROCESS FEEDBACK

If the need for Evidence Requests reveals a recurring system problem, the Researcher may also produce Process Feedback.

Examples:

- Job Experience Records repeatedly omit ownership.
- Records repeatedly omit attribution.
- Evidence Responses repeatedly lack a necessary factual dimension.
- The Evidence Request schema cannot express a recurring investigative need.
- The same class of uncertainty repeatedly causes avoidable rework.
- Record structure repeatedly makes reconciliation difficult.
- Existing contracts create recurring ambiguity.

Process Feedback should identify:

- Observed pattern.
- Operational impact.
- Suspected architectural layer.
- Relevant artifacts.
- Suggested area for Supervisor review.

Intended consumer:

    Supervisor

Process Feedback is separate from the Evidence Request.

Do not withhold the factual investigation artifact while waiting for system improvement.

---

# 15. VALIDATION

Before completing the task, verify:

- [ ] The factual issue is materially relevant.
- [ ] Reasonable existing-evidence retrieval was performed first.
- [ ] Existing direct evidence was reviewed.
- [ ] Existing transferable evidence was reviewed.
- [ ] Adjacent experience was reviewed.
- [ ] Previous Evidence Requests were reviewed.
- [ ] Previous Evidence Responses were reviewed.
- [ ] The deficiency requires factual development rather than Writer correction.
- [ ] The request identifies exactly what remains unknown.
- [ ] Existing evidence is summarized accurately.
- [ ] Promising professional contexts are identified.
- [ ] Facts that must not be assumed are explicit.
- [ ] Investigative objectives describe needed facts rather than dictating interview technique.
- [ ] Full-resolution criteria are defined.
- [ ] Partial-resolution criteria are defined.
- [ ] Transferable-resolution criteria are defined when applicable.
- [ ] Confirmed-gap criteria are defined.
- [ ] Analytical impact is stated.
- [ ] Claim constraints are stated when applicable.
- [ ] Current supported position is stated.
- [ ] No workflow or blocking state is assigned.
- [ ] The request does not lead the job hunter toward a desired claim.
- [ ] Duplicate requests were avoided.
- [ ] Related prior requests remain traceable.
- [ ] One request represents one coherent factual investigation.
- [ ] The output conforms to the Evidence Request schema.

---

# 16. COMPLETION CONDITION

The task is complete when the Researcher has converted a material factual evidence deficiency into a focused, traceable, neutral, and actionable Evidence Request that clearly establishes:

    What factual issue matters.

    What authoritative evidence already establishes.

    What remains unknown.

    Why the unknown information matters.

    Where the Interviewer should begin looking.

    What facts must not be assumed.

    What factual dimensions require investigation.

    What would fully resolve the issue.

    What would partially resolve it.

    What would establish transferable evidence.

    What would confirm a genuine gap.

    What analytical limitation remains while the issue is unresolved.

The Researcher must not use Evidence Requests as a substitute for thorough retrieval and analysis.

The task's governing transformation is:

    Search existing authoritative evidence
            ↓
    Evaluate evidence
            ↓
    Identify material factual deficiency
            ↓
    Define coherent factual investigation
            ↓
    Define resolution criteria
            ↓
    Define analytical impact
            ↓
    Produce Evidence Request

The task ends when the Evidence Request is complete.

How that artifact is transferred or acted upon is outside this task instruction.