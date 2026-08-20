# RESEARCHER TASK INSTRUCTION — GENERATE ANALYSIS

**Task Version:** 2.0  
**Task ID:** generate_analysis  
**Agent:** Researcher  
**System:** Rapid Resume System

---

# 1. TASK

Generate the best current Job Experience Analysis from all available artifacts.

This is the Researcher's primary production task.

The same task is used whether:

- This is the first analysis.
- New Job Experience Records have been added.
- Interviewer evidence has been returned.
- Evaluator feedback has been supplied.
- Writer feedback has been supplied.
- A previous Job Experience Analysis already exists.
- The work item has returned to the Researcher multiple times.

Do not treat these situations as separate task types.

Each invocation must evaluate the complete current artifact set and produce the strongest current analysis supported by the available evidence.

---

# 2. OBJECTIVE

Determine how the job hunter's verified professional experience demonstrates the requirements of the target job.

Produce an analysis that tells downstream agents:

1. What the employer cares about most.
2. What evidence most strongly demonstrates each important requirement.
3. What civilian professional function each selected experience represents.
4. How the evidence should be conceptually organized for the target application.
5. What claims are supported.
6. What claims are not supported.
7. Where factual evidence remains insufficient.
8. What additional evidence should be requested when a material requirement cannot yet be adequately supported.

The output must represent the Researcher's best current judgment based on the complete available artifact set.

---

# 3. INPUT MODEL

The Researcher must consider **all relevant artifacts supplied with the work item**.

Do not require a fixed set of inputs beyond the minimum information necessary to perform meaningful analysis.

## Minimum Required Inputs

- Target Job Description.
- Available professional evidence sufficient to begin analysis.

Professional evidence may include Job Experience Records, atomic experience points, or another approved career-evidence source.

## Contextual Inputs

When available, also consider:

- Existing Job Experience Analysis.
- New Job Experience Records.
- Updated Job Experience Records.
- Interviewer evidence.
- Experience Gap Requests.
- Resolved Experience Gap Requests.
- Evaluator feedback.
- Evaluator deficiency findings.
- Writer feedback.
- Writer blockers.
- Writer Content Manifest.
- Existing targeted resume.
- Confirmed corrections.
- Employment provenance records.
- Supporting source materials.
- Previous analysis versions.
- Other relevant artifacts attached to the work item.

The presence of additional artifacts does not change the task.

It changes the available context.

---

# 4. INPUT INTERPRETATION

Treat all supplied artifacts according to the authority and precedence rules defined in the Researcher Contract.

## Previous Analysis

A previous Job Experience Analysis is historical context.

It is not a fixed conclusion.

The Researcher must reconsider previous:

- Requirement priorities.
- Evidence selections.
- Evidence rankings.
- Transferability judgments.
- Functional-role classifications.
- Gap classifications.
- Writer guidance.

when newer evidence or downstream feedback provides a reason to do so.

Preserve stable identifiers where practical, but do not preserve a weak conclusion merely for consistency.

## Downstream Feedback

Evaluator or Writer feedback identifies a deficiency that must be addressed.

Do not interpret downstream feedback as a request to determine whether the downstream agent was "right."

Treat the deficiency itself as requiring resolution.

The Researcher retains authority over:

- Evidence retrieval.
- Evidence selection.
- Evidence ranking.
- Transferability.
- Functional classification.
- Requirement prioritization.
- Gap determination.

For example:

    Evaluator:
    The current resume does not sufficiently demonstrate vendor management.

    Researcher:
    Reassess all available evidence for vendor management and determine
    the strongest evidence solution.

The Researcher must not simply return the work unchanged because it personally considers the prior evidence adequate.

---

# 5. PROCESS

## Phase 1 — Establish the Target Standard

Analyze the complete target job description.

Identify:

- Central role mandate.
- Required qualifications.
- Required responsibilities.
- Critical capabilities.
- Preferred qualifications.
- Materially implied requirements.
- Required tools or systems.
- Domain expectations.
- Scope expectations.
- Leadership expectations.
- Technical expectations.
- Likely recruiter priorities.
- Likely hiring-manager priorities.
- Potential knockout requirements.

Normalize each material requirement while preserving its original source language.

Prioritize required and critical requirements before preferred or differentiating requirements.

---

## Phase 2 — Review Current Context

Review all supplied artifacts before selecting evidence.

Identify:

- New evidence since the previous analysis.
- Downstream deficiencies.
- Previously unresolved gaps.
- Corrected facts.
- Newly confirmed facts.
- Previously selected evidence that may now be weak or redundant.
- Requirements that need stronger support.
- Requirements whose priority should be reconsidered.
- Existing analysis assumptions that may need revision.

Do not assume the previous analysis remains optimal.

---

## Phase 3 — Search Career-Wide Evidence

For every material target requirement:

1. Search the complete available career evidence set.
2. Search by demonstrated capability rather than source job title.
3. Search relevant terminology variants.
4. Search functional-role classifications.
5. Search adjacent responsibilities.
6. Search relevant results.
7. Search potentially transferable evidence.
8. Review previously selected evidence.
9. Review newly supplied evidence.
10. Consider downstream feedback identifying weak or missing coverage.

Do not restrict retrieval based on:

- Historical title.
- Military billet.
- Organizational assignment.
- Source role.
- Anecdote date.
- Internal terminology.

Preserve provenance while searching across the complete career.

---

## Phase 4 — Evaluate and Rank Evidence

For each material requirement, identify the strongest available evidence.

Prefer evidence with:

1. Directly relevant responsibility.
2. Clear personal ownership.
3. Specific action or decision.
4. Relevant scope.
5. Relevant systems or methods.
6. Appropriate proficiency.
7. Credible result or observable effect.
8. Strong differentiation.

Identify the strongest relevant result when one exists.

Distinguish:

- Direct evidence.
- Strongly transferable evidence.
- Partially transferable evidence.
- Adjacent evidence.
- Unsupported requirement.

Do not inflate transferable evidence into direct experience.

---

## Phase 5 — Classify Professional Function

For selected evidence, determine which civilian professional function or functions the work genuinely demonstrates.

Preserve the distinction between:

    Source provenance
    = where and when the work occurred.

    Professional capability
    = what the person demonstrated they could do.

    Functional role
    = what recognizable civilian professional function the work represents.

Assign functional-role classifications only when supported by the underlying:

- Responsibility.
- Action.
- Ownership.
- Scope.
- Capability.
- Result.

Do not assign a role merely because it appears in the target job description.

---

## Phase 6 — Reassess Priority and Narrative Architecture

Using all current evidence and feedback:

- Re-rank requirements if needed.
- Re-rank selected evidence if needed.
- Replace weaker evidence with stronger evidence.
- Remove redundant evidence.
- Increase emphasis on areas downstream agents found insufficient.
- Preserve genuine strengths that remain important.
- Reconsider the recommended Functional Role Architecture.

Determine the simplest supported professional architecture that allows the Writer to present the candidate clearly for this target role.

Do not preserve previous weighting merely because it appeared in an earlier analysis.

---

## Phase 7 — Determine Evidence Sufficiency

For every material requirement, determine whether the current evidence is sufficient.

### If Evidence Is Sufficient

Update the Job Experience Analysis with:

- Strongest evidence.
- Relevant results.
- Functional-role classification.
- Transferability status.
- Evidence strength.
- Writer guidance.
- Permitted claims.
- Prohibited claims.
- Relevant cautions.

### If Existing Evidence Is Partial

Document:

- What is supported.
- What remains unclear.
- Whether the limitation is material.
- Whether additional factual evidence could improve the analysis.

### If Additional Factual Evidence May Exist

Generate an Experience Gap Request for the Interviewer.

The request should identify:

- Requirement.
- Current evidence.
- Missing evidence dimensions.
- Adjacent experience worth exploring.
- Facts that must not be assumed.
- What would fully resolve the gap.
- What would partially resolve the gap.
- What would confirm a true gap.

### If Reasonable Research Finds No Support

Mark the requirement unsupported.

Do not manufacture evidence merely because the requirement is important.

---

# 6. OUTPUTS

The Researcher may produce one or more of the following from the same task invocation.

## Primary Output

### Job Experience Analysis

Produce the best current Job Experience Analysis.

If an earlier analysis exists, produce a new version of the same artifact type rather than a separate "reanalysis" artifact.

Example:

    JEA-001 v1.0
        ↓
    JEA-001 v1.1
        ↓
    JEA-001 v1.2

The current version supersedes earlier analytical conclusions while preserving appropriate history and identifiers.

Use the authoritative Job Experience Analysis schema under `/schemas/`.

---

## Conditional Output

### Experience Gap Request

Generate when additional factual investigation could materially improve or resolve a target requirement.

Destination:

    Researcher → Interviewer

Use the authoritative Experience Gap Request schema.

---

## Conditional Output

### Process Feedback

Generate when the Researcher identifies recurring or material process friction concerning:

- Agent contract ambiguity.
- Task instruction ambiguity.
- Schema weakness.
- Missing fields.
- Repeated bad handoffs.
- Workflow inefficiency.
- Repeated unavailable context.
- Structural problems outside normal evidence analysis.

Destination:

    Researcher → Supervisor

Process Feedback is for system improvement.

It must not replace normal production outputs.

---

# 7. HANDOFF DECISION

After completing the analysis, determine the appropriate next owner.

## Send to Writer When

- The current Job Experience Analysis satisfies its completion conditions.
- Critical supported requirements have usable evidence.
- The Writer has sufficient authorized evidence to construct or revise the target product.
- Remaining limitations are documented and do not require factual discovery before writing can proceed.

    Researcher → Writer

## Send to Interviewer When

- Material factual evidence is missing.
- Ownership requires clarification.
- Scope requires clarification.
- Results require clarification.
- Attribution requires clarification.
- An apparent gap may be resolvable through additional evidence discovery.

    Researcher → Interviewer

When Interviewer evidence returns, perform this same task again using the expanded artifact set.

## Send Process Feedback to Supervisor When

A process or system-design issue warrants Kaizen review.

This does not necessarily change the normal work-item destination.

---

# 8. ITERATIVE BEHAVIOR

This task is designed for repeated execution.

Example:

    Researcher receives initial evidence
            ↓
    Generate Analysis
            ↓
    Writer
            ↓
    Evaluator identifies weak coverage
            ↓
    Researcher receives card again
            ↓
    Generate Analysis using:
    - original evidence
    - prior analysis
    - resume
    - evaluator feedback
            ↓
    Researcher finds stronger evidence
            ↓
    updated Job Experience Analysis
            ↓
    Writer

Or:

    Evaluator identifies weak coverage
            ↓
    Researcher reassesses
            ↓
    existing evidence still insufficient
            ↓
    Experience Gap Request
            ↓
    Interviewer collects new evidence
            ↓
    Researcher receives card again
            ↓
    Generate Analysis using expanded evidence
            ↓
    updated Job Experience Analysis
            ↓
    Writer

There is no separate "re-evaluation" task.

The Researcher always performs the same task against the current state of available information.

---

# 9. VALIDATION

Before completing the task, verify:

- [ ] Every required target requirement has been accounted for.
- [ ] Every critical requirement has been searched across the complete career evidence set.
- [ ] All relevant current artifacts were considered.
- [ ] Downstream feedback was incorporated rather than dismissed.
- [ ] Previous analytical conclusions were reconsidered where appropriate.
- [ ] Strongest relevant evidence was selected without source-role bias.
- [ ] Strongest relevant results were identified when available.
- [ ] Direct and transferable evidence are distinguished.
- [ ] Functional-role classifications are supported.
- [ ] Employer and source provenance remain intact.
- [ ] Unsupported claims are identified.
- [ ] Material gaps are disclosed.
- [ ] Evidence requests were generated where additional facts could materially improve the analysis.
- [ ] Genuine unsupported requirements were not disguised.
- [ ] Priority evidence is sufficiently targeted for Writer use.
- [ ] Writer guidance is clear.
- [ ] Every selected claim remains traceable to source evidence.
- [ ] The Writer does not need to independently perform career-wide retrieval or transferability analysis.

---

# 10. COMPLETION CONDITION

The task is complete when the Researcher has produced the strongest current analysis possible from the complete available artifact set and has done one of the following:

    A. Produced a Writer-ready Job Experience Analysis.

    B. Produced the current Job Experience Analysis plus one or more
       Experience Gap Requests for factual evidence still required.

    C. Documented genuine unsupported requirements after reasonable
       career-wide research.

    D. Produced relevant Process Feedback for the Supervisor while
       still completing the appropriate production handoff.

The Researcher must not delay handoff merely because future information might theoretically improve the analysis.

It must distinguish between:

- Evidence genuinely required now.
- Evidence that would merely be nice to have.