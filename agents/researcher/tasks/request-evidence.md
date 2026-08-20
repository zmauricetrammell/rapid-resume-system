# RESEARCHER TASK INSTRUCTION — REQUEST EVIDENCE

**Task Version:** 2.0  
**Task ID:** request_evidence  
**Agent:** Researcher  
**System:** Rapid Resume System

---

# 1. TASK

Generate an Experience Gap Request when the current evidence set is insufficient to adequately evaluate or support a material target-job requirement and additional factual evidence may exist.

This task converts an identified evidence deficiency into a focused request that the Interviewer can investigate with the job hunter.

The purpose is not to prove that the job hunter lacks the experience.

The purpose is to identify exactly what factual information is missing and give the Interviewer enough context to investigate it efficiently and neutrally.

Use this task when:

- A material requirement cannot be adequately supported from the current evidence set.
- Existing evidence appears relevant but lacks important detail.
- Ownership is unclear.
- Scope is unclear.
- Results are unclear.
- Attribution is unclear.
- Proficiency is unclear.
- Duration or frequency is unclear.
- Direct versus transferable experience cannot be established.
- A downstream agent has identified a material deficiency and the Researcher determines that new factual evidence is required to resolve it.
- Conflicting evidence requires clarification from the job hunter.
- A likely experience gap cannot yet be distinguished from incomplete documentation.

Do not use this task merely because stronger evidence would be nice to have.

---

# 2. OBJECTIVE

Produce a focused Experience Gap Request that enables the Interviewer to discover, clarify, or confirm the factual evidence needed to resolve a material requirement.

The request must tell the Interviewer:

1. Which requirement is affected.
2. Why the current evidence is insufficient.
3. What evidence already exists.
4. Which specific factual dimensions are missing.
5. Which adjacent experiences provide the best starting points.
6. What facts must not be assumed.
7. What questions or investigative directions are likely to be useful.
8. What would constitute full resolution.
9. What would constitute partial resolution.
10. What would confirm that the gap is genuine.

The request must be specific enough that the Interviewer does not need to repeat the Researcher's analysis.

---

# 3. INPUT MODEL

The Researcher must consider all relevant current artifacts before requesting new evidence.

## Minimum Required Inputs

- Target Job Description.
- Current professional evidence set.
- Identified material requirement or evidence deficiency.

## Contextual Inputs

When available, also consider:

- Current Job Experience Analysis.
- Previous Job Experience Analyses.
- Relevant Job Experience Records.
- Atomic experience points.
- Previous Experience Gap Requests.
- Previous Interviewer responses.
- Evaluator feedback.
- Writer feedback.
- Writer Content Manifest.
- Current targeted resume.
- Employment provenance records.
- Confirmed corrections.
- Supporting source materials.
- Other artifacts attached to the work item.

Before generating a request, the Researcher must determine that reasonable retrieval from the existing evidence set has already been attempted.

---

# 4. REQUEST THRESHOLD

Generate an Experience Gap Request only when all of the following are true:

- The affected requirement is material enough to justify additional investigation.
- The current evidence is insufficient for the Researcher's analysis.
- Reasonable career-wide retrieval has already been performed.
- Existing terminology variants and adjacent capabilities have been considered.
- Existing direct and transferable evidence has been evaluated.
- The missing information is factual rather than purely presentational.
- Additional questioning could plausibly resolve or materially clarify the deficiency.

Do not request evidence for:

- Formatting issues.
- Resume phrasing issues.
- Content-ordering issues.
- Keyword placement issues.
- Evidence that already exists but merely needs better selection.
- Evidence that already exists but merely needs better presentation.
- Low-priority details unlikely to affect the target-job analysis.
- Confirmed gaps that have already been adequately investigated.

---

# 5. PROCESS

## Phase 1 — Identify the Requirement

Identify the specific target-job requirement affected.

Preserve:

- Requirement ID.
- Original job-description language.
- Normalized requirement.
- Requirement priority.
- Whether it is required, preferred, or materially implied.

Determine why the requirement matters to the target role.

---

## Phase 2 — Review Existing Evidence

Identify all currently available evidence relevant to the requirement.

Include:

- Direct evidence.
- Transferable evidence.
- Adjacent evidence.
- Relevant results.
- Relevant responsibilities.
- Relevant tools or systems.
- Relevant functional-role classifications.
- Previous evidence requests and responses.

Summarize what the existing evidence already establishes.

Do not ask the Interviewer to rediscover facts that are already documented.

---

## Phase 3 — Identify the Deficiency

Define precisely what remains unknown or insufficient.

Possible evidence dimensions include:

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

Avoid vague statements such as:

- "Need more detail."
- "Need stronger evidence."
- "Need leadership experience."
- "Need better metrics."

State exactly what information is missing.

---

## Phase 4 — Identify Adjacent Experience

Identify the strongest existing professional experiences that may contain the missing evidence.

For each promising starting point, provide:

- Experience or record ID.
- Relevant role or employment context.
- What is already known.
- Why the experience may contain the missing evidence.
- Which dimensions should be explored further.

The Interviewer should begin with the most promising existing context before searching broadly.

Do not imply that adjacent evidence proves the missing fact.

---

## Phase 5 — Define Facts That Must Not Be Assumed

Explicitly identify facts the Interviewer must not infer or lead the job hunter toward.

Examples:

- Do not assume coordination means ownership.
- Do not assume leadership means direct reports.
- Do not assume tool familiarity means production administration.
- Do not assume team results were individually attributable.
- Do not assume a similar system is equivalent to the required system.
- Do not assume military authority is equivalent to a specific civilian management responsibility.
- Do not assume a result was measured if no measurement exists.
- Do not assume direct experience when only transferable evidence exists.

These constraints protect factual integrity during the interview.

---

## Phase 6 — Develop Investigation Guidance

Provide the Interviewer with neutral investigative directions.

Questions should help discover facts rather than steer the job hunter toward a preferred answer.

Good examples:

    What part of the vendor relationship were you personally responsible for?

    Were you responsible for measuring or enforcing service levels,
    or were you primarily coordinating with the vendor?

    How many vendors or contracts were involved?

    What happened when performance fell below expectations?

    Did you personally make renewal, escalation, or corrective-action decisions?

    Was the result formally measured or observed qualitatively?

Avoid leading questions such as:

    You managed the vendor SLA directly, correct?

    Can we say you owned vendor performance?

    Would it be fair to call this contract management?

The Interviewer owns the final questioning strategy.

The Researcher provides investigative context, not a script that forces a conclusion.

---

# 6. RESOLUTION CRITERIA

Every Experience Gap Request must define clear resolution criteria.

## Full Resolution

Define the evidence that would adequately establish the requirement.

Example:

    Full resolution requires confirmed evidence that the job hunter
    personally owned or materially led vendor performance management,
    including responsibility for service expectations, escalation,
    corrective action, or performance review.

Full resolution does not require a specific answer if several factual paths could establish the capability.

---

## Partial Resolution

Define evidence that would improve support but leave a meaningful limitation.

Example:

    Partial resolution exists if the job hunter coordinated vendor
    performance or escalations but did not own SLA definition,
    enforcement, or contract decisions.

Partial resolution should identify the remaining limitation.

---

## Transferable Resolution

When appropriate, define what evidence would establish transferable rather than direct experience.

Example:

    Transferable resolution exists if the job hunter managed internal
    service-performance targets using substantially similar governance
    and escalation practices but did not directly manage external vendors.

Do not collapse transferable resolution into direct resolution.

---

## Confirmed Gap

Define what would establish that the job hunter does not possess the requested experience.

Example:

    Confirmed gap exists if the job hunter confirms that they did not
    own, lead, materially support, or perform comparable vendor-performance
    responsibilities in any relevant role.

The answer:

    "I do not have that experience."

is a valid resolution.

---

# 7. OUTPUT

Produce an Experience Gap Request conforming to the authoritative schema under:

    /schemas/experience-gap-request.yaml

The request should include, at minimum:

- Request ID.
- Target Job ID.
- Requirement ID.
- Requirement priority.
- Original requirement language.
- Normalized requirement.
- Reason for request.
- Current evidence summary.
- Missing evidence dimensions.
- Adjacent experience references.
- Investigation guidance.
- Facts that must not be assumed.
- Full-resolution criteria.
- Partial-resolution criteria.
- Transferable-resolution criteria when applicable.
- Confirmed-gap criteria.
- Blocking status.
- Originating artifact references.

---

# 8. HANDOFF

The normal destination is:

    Researcher → Interviewer

The Interviewer owns:

- Human questioning.
- Memory prompting.
- Fact discovery.
- Clarification.
- Confirmation.
- Job Experience Record creation or revision.

The Researcher does not dictate the factual answer.

After the Interviewer completes the investigation, the work item should return to the Researcher with:

- New or updated Job Experience Records.
- Resolved Experience Gap Request.
- Confirmed uncertainty.
- Partial evidence.
- Transferable evidence.
- Or confirmed lack of experience.

The Researcher then performs:

    generate_analysis

again using the expanded artifact set.

---

# 9. MULTIPLE EVIDENCE REQUESTS

A single Researcher invocation may identify more than one material evidence deficiency.

Generate separate Experience Gap Requests when the missing evidence concerns materially distinct:

- Requirements.
- Professional capabilities.
- Experiences.
- Ownership questions.
- Scope questions.
- Results questions.

Do not combine unrelated evidence gaps into one large Interviewer request merely for convenience.

However, closely related missing dimensions concerning the same professional episode may remain within one request.

Prefer the smallest set of requests that allows focused investigation.

---

# 10. DUPLICATE AND REPEAT REQUEST CONTROL

Before generating a new request:

1. Check whether the same requirement has previously generated an Experience Gap Request.
2. Review the previous request.
3. Review the Interviewer's response.
4. Determine whether the current deficiency is genuinely new.
5. Do not repeatedly ask the same factual question after it has been resolved or confirmed as a gap.

A new request may be appropriate when:

- New evidence changes the question.
- Downstream feedback reveals a different missing dimension.
- A previous partial resolution exposes a narrower factual issue.
- Conflicting evidence emerges.
- The prior request did not investigate the current requirement dimension.

When a request is related to a prior request, preserve traceability.

---

# 11. BLOCKING DECISION

Determine whether the evidence request blocks progression to the Writer.

## Blocking Request

Mark the request as blocking when the missing evidence materially affects:

- A critical required qualification.
- A likely knockout requirement.
- A central responsibility.
- A material credibility issue.
- A claim the Writer cannot safely make without clarification.
- The target professional identity.
- A major fit determination.

When blocking:

    Researcher → Interviewer

The work item should return to the Researcher before proceeding to Writer.

---

## Non-Blocking Request

Mark the request as non-blocking when:

- Current evidence adequately supports the critical requirements.
- Additional evidence would improve differentiation rather than establish basic fit.
- The missing detail concerns a lower-priority preferred qualification.
- The Writer can proceed safely using the current authorized evidence.

When non-blocking, the workflow may permit:

    Researcher → Writer

while the evidence request remains available for later development.

The workflow implementation determines whether non-blocking requests are processed immediately or retained as improvement opportunities.

---

# 12. PROCESS FEEDBACK

If the need for an evidence request reveals a recurring system problem rather than an isolated evidence gap, the Researcher may also generate Process Feedback.

Examples:

- The same factual dimension is repeatedly missing from Job Experience Records.
- The Interviewer schema does not capture an evidence dimension the Researcher frequently needs.
- The same class of requirement repeatedly creates avoidable handoff cycles.
- Experience records systematically omit ownership.
- Functional-role classifications repeatedly lack enough supporting context.
- A schema field is ambiguous.
- The workflow repeatedly loses returned evidence.

Destination:

    Researcher → Supervisor

Process Feedback does not replace the Experience Gap Request.

The production issue and the system-improvement issue are separate outputs.

---

# 13. VALIDATION

Before completing the task, verify:

- [ ] The requirement is materially relevant to the target job.
- [ ] Reasonable existing-evidence retrieval was performed first.
- [ ] Existing direct evidence was reviewed.
- [ ] Existing transferable evidence was reviewed.
- [ ] Adjacent experience was reviewed.
- [ ] The deficiency requires factual development rather than Writer correction.
- [ ] The request identifies exactly what evidence is missing.
- [ ] Existing evidence is summarized so the Interviewer does not duplicate research.
- [ ] Promising adjacent experiences are identified.
- [ ] Facts that must not be assumed are explicit.
- [ ] Investigation guidance is neutral.
- [ ] Full-resolution criteria are defined.
- [ ] Partial-resolution criteria are defined.
- [ ] Transferable-resolution criteria are defined when applicable.
- [ ] Confirmed-gap criteria are defined.
- [ ] The request does not lead the job hunter toward a desired claim.
- [ ] Previous requests were reviewed for duplication.
- [ ] Blocking status is appropriate.
- [ ] Source and requirement identifiers are preserved.
- [ ] The output conforms to the Experience Gap Request schema.

---

# 14. COMPLETION CONDITION

The task is complete when the Researcher has converted a material evidence deficiency into a focused, traceable, neutral, and actionable Experience Gap Request that the Interviewer can investigate without independently repeating the Researcher's analysis.

The completed request must make clear:

    What requirement matters.

    What is already known.

    What is still missing.

    Where the Interviewer should begin.

    What must not be assumed.

    What would resolve the issue.

    What would partially resolve it.

    What would confirm a genuine gap.

The Researcher must not use evidence requests as a substitute for thorough retrieval.

The correct sequence is:

    Search existing evidence
            ↓
    Evaluate evidence
            ↓
    Identify material factual deficiency
            ↓
    Request evidence
            ↓
    Interviewer develops or confirms facts
            ↓
    Researcher generates analysis again