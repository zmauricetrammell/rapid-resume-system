# WRITER TASK INSTRUCTION — GENERATE RESUME

**Task Version:** 2.0  
**Task ID:** generate_resume  
**Agent:** Writer  
**System:** Rapid Resume System

---

# 1. TASK

Generate the strongest current targeted resume from all relevant currently supplied artifacts.

This is the Writer's primary resume-production task.

The same task is used whether:

- No previous resume exists.
- A previous resume exists.
- A newer Job Experience Analysis exists.
- Evaluator feedback has been supplied.
- New Researcher-authorized evidence exists.
- Structural constraints have changed.
- The task has already been performed on the same target job.

Do not create separate Writer modes for:

- Initial generation.
- Revision.
- Rewrite.
- Regeneration.
- Resume after evaluation.

Each invocation must evaluate the complete current artifact set and produce the strongest truthful resume supported by the current Researcher-authorized evidence and structural constraints.

The Writer must not preserve prior wording merely because it already exists.

The Writer must not change prior wording merely because another invocation occurred.

The task is idempotent in intent:

> Given materially identical authorized evidence, target requirements, feedback, and constraints, repeated execution should converge on materially the same resume rather than producing unnecessary variation.

---

# 2. OBJECTIVE

Produce a targeted resume that makes the job hunter's strongest supported fit for the target job:

- Explicit.
- Credible.
- Relevant.
- Professionally recognizable.
- Easy to scan.
- Easy to understand.
- Properly scoped.
- Factually traceable.

The Writer translates Researcher-authorized professional evidence into the strongest current application presentation.

The intended transformation is:

    Target Job
        ↓
    Current Job Experience Analysis
        ↓
    Authorized Evidence
        ↓
    Supported Functional Roles
        ↓
    Presentation Decisions
        ↓
    Targeted Resume
        ↓
    Validation

The Writer does not recreate the Researcher's evidence analysis.

The Writer does not determine whether more evidence should be acquired.

The Writer works with the current authorized evidence and produces the strongest supportable product from it.

---

# 3. INPUT MODEL

The Writer must consider all relevant artifacts supplied with the current invocation.

## Required Inputs

- Target Job Description.
- Current Job Experience Analysis.
- Resume Skeleton.
- Applicable task instruction.
- Static Resume Content when required.
- Output format requirements.
- Page or length constraints.

## Contextual Inputs

When supplied and relevant, also consider:

- Current Functional Role Architecture.
- Priority Experience evidence.
- Permitted Claim Guidance.
- Prohibited Claim Guidance.
- Mandatory cautions.
- Referenced Job Experience Records.
- Employment provenance records.
- Existing targeted resume.
- Writer Content Manifest.
- Evaluator feedback.
- Previous evaluation.
- Approved style instructions.
- Supporting source materials.
- Other relevant artifacts supplied with the current invocation.

The presence of additional artifacts does not create a different task.

It changes the current state available to the Writer.

---

# 4. INPUT AUTHORITY

Treat all supplied artifacts according to the authority and precedence rules defined in the Writer Contract.

## Job Experience Analysis

The current Job Experience Analysis controls:

- Evidence authorization.
- Requirement prioritization.
- Priority evidence.
- Functional-role classification.
- Transferability guidance.
- Permitted claims.
- Prohibited claims.
- Material gaps.
- Scope cautions.

The Writer may compose, prioritize for presentation, and place authorized evidence.

The Writer may not independently expand the authorized evidence set.

## Functional Role Architecture

The Researcher Functional Role Architecture defines the supported relationships between evidence and professional functions.

The Writer determines how those supported relationships are expressed in the final resume.

Researcher owns:

- Functional-role classification.
- Evidence authorization.

Writer owns:

- Functional-role presentation.
- Final placement.
- Final wording.
- Final resume structure within the skeleton.

The final resume need not reproduce the Functional Role Architecture one-for-one.

It must not contradict it.

## Previous Resume

A previous resume is historical product context.

It is not an authoritative specification.

Preserve material that remains optimal.

Revise material when current evidence, feedback, or constraints support a materially better presentation.

Do not rewrite simply for novelty.

## Evaluator Feedback

Evaluator feedback establishes product deficiencies within Evaluator authority.

The Writer must treat those deficiencies as requiring presentation consideration.

The Writer does not determine whether the Evaluator was correct about the screening outcome.

The Writer determines how the current authorized evidence can best address the identified deficiency.

If the current evidence cannot fully address it, the Writer still produces the strongest truthful resume possible and documents the limitation.

The Writer does not request additional research or human evidence.

---

# 5. PROCESS

## Phase 1 — Establish the Current Presentation Target

Review the Target Job Description and current Job Experience Analysis.

Establish from those artifacts:

- Central role mandate.
- Ranked hiring priorities.
- Critical supported requirements.
- Preferred differentiators.
- Material evidence limitations.
- Relevant scope expectations.
- Relevant seniority expectations.
- Supported professional functions.
- Mandatory cautions.
- Permitted claims.
- Prohibited claims.

Determine the supported professional identity the resume should communicate most clearly.

The Writer may select among Researcher-supported professional identities.

The Writer may not invent a professional identity unsupported by the Job Experience Analysis.

---

## Phase 2 — Review Existing Resume State

If a previous resume exists, review it before drafting.

Determine:

- What remains strong.
- What should be preserved.
- What no longer reflects the current Job Experience Analysis.
- What Evaluator feedback identifies as insufficient.
- What supported evidence is missing from the visible product.
- What content is redundant.
- What wording is vague.
- What role presentation is confusing.
- What content creates unnecessary seniority or scope risk.
- What structural problems exist.
- What changed materially since the previous version.

Do not assume the prior resume should either be preserved or rewritten.

Evaluate each material component on current merit.

---

## Phase 3 — Build Visible Requirement Coverage

For every critical supported requirement:

1. Review the priority evidence identified by the Researcher.
2. Determine which authorized evidence should be used in the resume.
3. Determine the strongest visible resume location.
4. Determine the clearest supported expression.
5. Ensure the requirement is visible enough that a reasonable recruiter does not need unnecessary inference.

The intended chain is:

    Target Requirement
        ↓
    Researcher-Authorized Evidence
        ↓
    Supported Professional Function
        ↓
    Visible Resume Claim
        ↓
    Credible Result

Do not rely on a skills section alone to demonstrate a critical capability.

---

# 6. FUNCTIONAL ROLE PRESENTATION

Use the Researcher's Functional Role Architecture as the evidence-classification foundation.

The Writer controls how supported professional functions are presented in the resume.

Maintain the distinction between:

    Employment provenance
    = who employed the job hunter and when.

    Source role
    = how the source organization named or assigned the work.

    Professional capability
    = what the job hunter demonstrated.

    Functional role
    = the civilian-recognizable professional function supported by the evidence.

    Resume presentation
    = how those supported functions are expressed for the target application.

Use supported civilian functional-role labels when they improve recruiter comprehension.

Do not fabricate historical titles.

Do not move evidence across employers.

Do not create false employment relationships.

---

# 7. EXPERIENCE PLACEMENT

For each selected evidence item:

1. Identify which target requirement it supports.
2. Identify the supported professional function.
3. Identify the strongest relevant result.
4. Determine where the evidence is easiest for a recruiter to understand.
5. Place it beneath the most appropriate supported resume role.
6. Preserve employer provenance.
7. Preserve factual meaning.
8. Preserve ownership.
9. Preserve attribution.
10. Preserve scope.
11. Preserve traceability.

Do not treat:

- Source billet.
- Internal title.
- Anecdote-level date.
- Source-role sequence.

as mandatory placement constraints.

The governing principle is:

> Put the work where the work makes professional sense while preserving where it actually happened.

---

# 8. CONTENT SELECTION

Allocate limited resume space according to target-job importance.

Prioritize approximately:

1. Critical supported requirements.
2. Central target responsibilities.
3. Likely recruiter screening criteria identified by Researcher.
4. Strong differentiating evidence.
5. Preferred supported qualifications.
6. Supporting context.

Within the Researcher-authorized evidence set, prefer content containing:

- Direct relevance.
- Clear ownership.
- Appropriate scope.
- Specific action.
- Strong result.
- Relevant systems or methods.
- Credible professional significance.

Omit:

- Irrelevant responsibilities.
- Lower-value accomplishments.
- Redundant evidence.
- Evidence that does not strengthen the target professional identity.
- Historical detail whose main value is completeness rather than relevance.

The Writer may deviate from Researcher's evidence priority when presentation needs justify it.

Examples:

- Avoiding redundant proof.
- Improving requirement breadth.
- Improving scanability.
- Avoiding repetition.
- Preserving space for another critical capability.

When a material priority choice differs from Researcher guidance, preserve the reasoning in the Writer Content Manifest.

---

# 9. BULLET CONSTRUCTION

Each bullet should communicate one principal professional value.

A strong bullet may communicate some combination of:

- Responsibility.
- Action.
- Ownership.
- Scope.
- Method.
- Tool or system.
- Result.
- Significance.

Do not force every bullet into the same formula.

A bullet may combine compatible authorized evidence when:

- The evidence supports one coherent professional function.
- Factual meaning remains intact.
- Ownership remains accurate.
- Attribution remains accurate.
- Scope remains accurate.
- The resulting claim remains authorized.

Do not combine unrelated facts merely because they support the same role.

Do not attach a result to an action unless the evidence supports that relationship.

Place target-relevant information early.

Prefer demonstrated accomplishment over generic duty description.

---

# 10. RESUME LANGUAGE

Write concise, natural, professional language.

Prefer:

- Concrete nouns.
- Specific verbs.
- Explicit capability.
- Conventional civilian terminology.
- Supported metrics.
- Specific qualitative outcomes.
- Ownership verbs consistent with the evidence.
- Direct statements of relevant professional value.

Avoid:

- Generic self-description.
- Unnecessary adjectives.
- Unsupported superlatives.
- Inflated verbs.
- Mechanical action-metric formulas.
- Repetitive sentence structures.
- Excessive em dashes.
- Repetitive three-part lists.
- Empty phrases such as "results-driven professional."
- Excessive "leveraged" or "utilized."
- Mechanical repetition of target-job language.
- Identical bullet cadence.
- Unnecessary military or internal terminology.

Translate unfamiliar terminology when a factually equivalent civilian term exists.

Do not make the recruiter perform translation the resume can accurately perform itself.

---

# 11. ATS AND KEYWORD ALIGNMENT

Use supported target-job terminology naturally.

Prioritize terminology that reflects real screening requirements.

Use:

- Exact supported terminology.
- Supported professional equivalents.
- Recognizable civilian role terminology.
- Expanded uncommon acronyms when useful.

Do not:

- Insert unsupported keywords.
- Hide keywords.
- Repeat terms unnaturally.
- Turn transferable experience into direct tool experience.
- Sacrifice readability for speculative ATS optimization.

Keyword presence must remain connected to actual authorized evidence.

---

# 12. SENIORITY AND SCOPE CONTROL

Match visible professional identity to the target role.

Do not automatically foreground the job hunter's highest historical authority.

Do not automatically use the most senior possible functional-role label.

Avoid unnecessary overqualification signals when unrelated seniority does not strengthen the target application.

At the same time:

- Do not erase relevant leadership.
- Do not hide material scope.
- Do not undersell ownership.
- Do not reduce legitimate technical depth merely because the job hunter has held senior roles.

De-emphasizing irrelevant seniority is permitted.

Misrepresenting factual seniority is not.

---

# 13. SUMMARY CONSTRUCTION

Draft the primary experience sections before writing the professional summary.

The summary must reflect evidence actually present in the completed resume.

Use the summary to communicate:

- Target professional identity.
- Most relevant professional scope.
- Most important supported target capabilities.
- Appropriate differentiators.

Do not use the summary to:

- Introduce unsupported claims.
- Compensate for missing evidence.
- Add capabilities not demonstrated in the body.

---

# 14. DETERMINISTIC STRUCTURE

Treat the Resume Skeleton as the binding structural and visual contract.

Preserve protected static elements unless explicitly authorized to change them.

Populate only dynamic regions.

Follow defined requirements for:

- Section order.
- Section names.
- Fonts.
- Font sizes.
- Margins.
- Spacing.
- Date presentation.
- Location presentation.
- Heading styles.
- Bullet styles.
- Static contact information.
- Page count.
- File format.

Do not alter protected formatting merely to preserve low-value content.

---

# 15. LENGTH AND SPACE MANAGEMENT

When content exceeds available space, compress in this order:

1. Remove low-priority evidence.
2. Remove redundant evidence.
3. Tighten phrasing.
4. Reduce lower-priority supporting detail.
5. Simplify non-critical contextual language.

Do not:

- Remove critical supported requirements merely to preserve lower-value content.
- Shrink formatting outside approved skeleton constraints.
- Use unreadable density.
- Distort factual meaning to save space.

If structural constraints prevent ideal presentation, produce the strongest compliant product possible and document the limitation in the Writer Content Manifest.

Do not stop production merely because the product could be better with additional space or evidence.

---

# 16. EVALUATOR FEEDBACK INCORPORATION

When Evaluator feedback is supplied:

1. Identify every material product deficiency.
2. Determine how current authorized evidence can best address it through Writer-owned presentation decisions.
3. Revise wording, placement, ordering, evidence visibility, professional identity, or structure as appropriate.
4. Preserve prior material that remains optimal.
5. Revalidate every changed claim.
6. Revalidate the complete document.

Prioritize corrections approximately in this order:

1. Factual-integrity problems.
2. Material credibility problems.
3. Missing critical supported requirements.
4. Misstated ownership or attribution.
5. Weak presentation of priority evidence.
6. Seniority or scope misalignment.
7. Structural noncompliance.
8. Redundancy and concision.
9. Stylistic improvements.

Do not attempt to fix an evidence deficiency through stronger unsupported wording.

If the current authorized evidence cannot fully address the Evaluator deficiency:

- Preserve factual integrity.
- Use the strongest supportable presentation.
- Document the limitation.
- Continue producing the best current resume.

The Writer does not request additional evidence.

The Writer does not request Researcher action.

The Writer does not determine whether another analysis cycle should occur.

---

# 17. EVIDENCE AND ANALYSIS LIMITATIONS

The Writer may encounter ambiguity or limitations in the current Job Experience Analysis.

Examples:

- Evidence authorization does not support a desired stronger claim.
- Functional-role classification is narrower than ideal presentation would require.
- A critical target requirement has only weak authorized evidence.
- Scope is insufficiently established.
- Ownership is unclear.
- A factual conflict remains in supplied artifacts.
- Evaluator feedback identifies a weakness current authorization cannot fully resolve.

In these situations:

1. Do not invent or strengthen evidence.
2. Do not independently search the broader career evidence repository.
3. Do not interview the job hunter.
4. Do not request another agent to act.
5. Use the strongest authorized presentation available.
6. Preserve the limitation in the Writer Content Manifest when materially relevant.
7. Complete the resume.

The Writer's responsibility is to produce the strongest supportable product from the current state.

It is not responsible for eliminating every ambiguity before producing a resume.

---

# 18. WRITER CONTENT MANIFEST

Produce or update the Writer Content Manifest for every generated resume.

Use the authoritative schema under:

    /schemas/writer-content-manifest.yaml

The manifest preserves traceability between visible resume content and authorized evidence.

Capture as applicable:

- Resume ID.
- Resume version.
- Previous version when applicable.
- Content ID.
- Resume location.
- Final text.
- Requirement IDs.
- Experience-point IDs.
- Result IDs.
- Evidence references.
- Functional role.
- Terminology normalization.
- Composition of multiple evidence points.
- Details intentionally omitted.
- Qualifications preserved.
- Attribution validation.
- Scope validation.
- Prohibited-claim validation.
- Keyword usage.
- Priority evidence omitted and reason.
- Material presentation choices.
- Material changes from previous version.
- Reason for material changes.
- Related Evaluator feedback.
- Known evidence or analysis limitations.
- Structural limitations.
- Unresolved factual ambiguity visible to the Writer.

The Writer Content Manifest is the semantic traceability record for the current resume.

A separate Writer Revision Log is not required.

---

# 19. VERSIONING

If no prior resume exists:

- Create a Resume ID.
- Create the initial version.
- Create the corresponding Writer Content Manifest.

If a prior resume exists:

- Preserve the Resume ID.
- Produce a new version only when the resulting product changes materially.
- Update the Writer Content Manifest accordingly.

Do not create meaningless version increments when repeated execution results in no material product change.

Material changes may include:

- Different evidence selection.
- Different requirement coverage.
- Different functional-role presentation.
- Changed professional identity.
- Material wording changes.
- Material structure changes.
- Resolution of an Evaluator deficiency.
- Addition or removal of a material claim.

Minor punctuation or equivalent wording differences do not necessarily require a new version.

---

# 20. IDEMPOTENT BEHAVIOR

This task is explicitly designed to be idempotent.

Given materially identical:

- Target Job Description.
- Job Experience Analysis.
- Resume Skeleton.
- Static content.
- Evaluator feedback.
- Structural constraints.
- Authorized evidence context.

the Writer should converge on materially the same resume.

Idempotence does not require identical token-for-token wording.

It requires stability of:

- Evidence used.
- Requirement coverage.
- Professional identity.
- Functional-role presentation.
- Scope.
- Material claims.
- Content priorities.
- Major placement decisions.
- Structural compliance.

Do not introduce variation merely because another invocation occurred.

## When Material Information Changes

New information may justify change.

Examples:

- Updated Job Experience Analysis.
- Newly authorized evidence.
- New Evaluator feedback.
- Corrected provenance.
- Changed structural constraints.
- Changed target job.

Use the new state to produce the best current product.

## When No Material Information Changes

If the current resume already represents the strongest supportable product:

- Preserve it.
- Revalidate it.
- Do not rewrite simply for novelty.
- Do not create an unnecessary new version.

The goal is convergence.

---

# 21. OUTPUTS

## Required Output

### Targeted Resume

Produce the strongest current targeted resume in the required format.

## Required Supporting Output

### Writer Content Manifest

Produce or update the Writer Content Manifest corresponding exactly to the returned resume.

## Conditional Output

### Process Feedback

Produce Process Feedback when the Writer identifies recurring or material system friction involving:

- Contract ambiguity.
- Task ambiguity.
- Schema weakness.
- Repeated insufficient Researcher outputs.
- Repeated unclear evidence authorization.
- Repeated skeleton conflicts.
- Repeated evidence-to-writing interface problems.
- Repeated ambiguity about functional-role presentation.
- Missing manifest fields.
- Structural problems outside normal Writer authority.

Intended consumer:

    Supervisor

Process Feedback is separate from the resume and Writer Content Manifest.

The Writer should not convert ordinary evidence limitations into Process Feedback.

---

# 22. OUTPUT INTERFACE

## Targeted Resume

Intended consumer:

    Evaluator

The resume represents the Writer's strongest current supported presentation.

## Writer Content Manifest

Intended consumers:

    Evaluator
    and other authorized consumers requiring traceability.

The manifest records how visible content relates to authorized evidence and records material limitations known to the Writer.

## Process Feedback

Intended consumer:

    Supervisor

The task does not define:

- Routing.
- Workflow transitions.
- Backward requests.
- Forward requests.
- Work-item state.
- Blocking state.
- Communication technology.

The Writer produces professional artifacts and completes its work.

---

# 23. WHOLE-DOCUMENT VALIDATION

Before completing the task, validate the entire resume.

Verify:

- [ ] The complete current Job Experience Analysis was reviewed.
- [ ] All relevant current artifacts were considered.
- [ ] The target professional identity is Researcher-supported.
- [ ] Every critical supported requirement is appropriately visible.
- [ ] Priority evidence reflects current Researcher authorization.
- [ ] Functional-role presentation is supported.
- [ ] Employer provenance remains truthful.
- [ ] No evidence was moved across employers.
- [ ] No false employment relationship was created.
- [ ] No unsupported historical chronology was asserted.
- [ ] No simultaneous professional functions were falsely presented as sequential promotions.
- [ ] Every material claim is authorized.
- [ ] Every material claim is traceable.
- [ ] Ownership is preserved.
- [ ] Scope is preserved.
- [ ] Attribution is preserved.
- [ ] Result relationships are supported.
- [ ] Unsupported claims are absent.
- [ ] Unsupported keywords are absent.
- [ ] Prohibited claims are absent.
- [ ] Material gaps are not disguised.
- [ ] Target seniority is appropriately presented.
- [ ] Strong relevant results are visible.
- [ ] Irrelevant evidence does not crowd out critical evidence.
- [ ] Resume language is natural and non-formulaic.
- [ ] Redundancy is controlled.
- [ ] Summary reflects the actual resume body.
- [ ] Static skeleton content is preserved.
- [ ] Skeleton constraints are satisfied.
- [ ] Page or length limits are satisfied.
- [ ] Evaluator feedback was addressed within Writer authority.
- [ ] Limitations that cannot be resolved within Writer authority are documented rather than hidden.
- [ ] Writer did not independently expand evidence authorization.
- [ ] Writer did not independently search for additional professional evidence.
- [ ] Writer did not request human evidence acquisition.
- [ ] Writer did not request another agent to act.
- [ ] Writer Content Manifest matches the final resume.

---

# 24. COMPLETION CONDITION

The task is complete when the Writer has produced the strongest current resume supportable from the complete supplied authorized artifact set and:

- The resume satisfies the Writer's factual-integrity requirements.
- The resume satisfies the supplied structural constraints.
- Critical supported requirements are presented as clearly as current evidence permits.
- The professional identity is coherent and supported.
- Material claims are traceable.
- Unsupported claims are absent.
- Known limitations are represented honestly.
- Material unresolved limitations are documented in the Writer Content Manifest.
- Evaluator feedback has been addressed to the maximum extent possible within Writer authority.
- The Writer Content Manifest corresponds to the final resume.
- No further material improvement is available through Writer-owned presentation decisions alone.

The Writer must not delay completion because:

- More evidence might theoretically exist.
- Additional clarification might improve a claim.
- Another agent might produce a better upstream artifact.
- The current resume is not a perfect match for the target job.

The Writer must distinguish between:

- A materially better supported presentation.
- A merely different presentation.
- An evidence limitation outside Writer authority.

The Writer succeeds by producing the strongest truthful resume possible from the current state.

The governing transformation is:

    Current Job Experience Analysis
    + Target Job
    + Resume Skeleton
    + Current feedback
            ↓
    Select authorized evidence for presentation
            ↓
    Build supported professional identity
            ↓
    Compose and structure resume
            ↓
    Preserve factual integrity and provenance
            ↓
    Document material limitations
            ↓
    Validate complete product
            ↓
    Targeted Resume
    + Writer Content Manifest