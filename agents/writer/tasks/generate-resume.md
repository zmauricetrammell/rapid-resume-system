# WRITER TASK INSTRUCTION — GENERATE RESUME

**Task Version:** 2.0  
**Task ID:** generate_resume  
**Agent:** Writer  
**System:** Rapid Resume System

---

# 1. TASK

Generate the best current targeted resume from all available artifacts.

This is the Writer's primary resume-production task.

The same task is used whether:

- No previous resume exists.
- A previous resume already exists.
- Evaluator feedback has been supplied.
- A new Job Experience Analysis has been supplied.
- New evidence has been incorporated by the Researcher.
- Writer feedback or blockers have been returned.
- The work item has returned to the Writer multiple times.
- The current resume requires substantial revision.
- The current resume requires only minor revision.

Do not treat initial generation and revision as separate task types.

Each invocation must evaluate the complete current artifact set and produce the strongest current resume supported by the available evidence and system constraints.

The Writer must not preserve previous wording merely because it already exists.

The Writer must not rewrite material that remains optimal merely because the task has been invoked again.

The task is idempotent in intent:

> Given the same authoritative inputs and constraints, repeated execution should converge on materially the same resume rather than producing unnecessary variation.

---

# 2. OBJECTIVE

Create the strongest truthful targeted resume supported by the current Job Experience Analysis and associated artifacts.

The resume must make the job hunter's fit for the target job:

- Explicit.
- Credible.
- Relevant.
- Professionally recognizable.
- Easy to scan.
- Easy to understand.
- Properly scoped.
- Factually traceable.

The Writer must translate the job hunter's demonstrated professional experience into a civilian-recognizable professional narrative without altering factual provenance.

The intended composition process is:

    Target Job
        ↓
    Required Capabilities
        ↓
    Current Job Experience Analysis
        ↓
    Priority Evidence
        ↓
    Functional Role Architecture
        ↓
    Logical Role Placement
        ↓
    Targeted Resume
        ↓
    Validation

The Writer's job is not to recreate the Researcher's analysis.

The Writer's job is to turn the Researcher's authorized evidence into the strongest current resume product.

---

# 3. INPUT MODEL

The Writer must consider **all relevant artifacts supplied with the work item**.

The presence of additional artifacts does not create a different task.

It changes the available context.

## Minimum Required Inputs

- Target Job Description.
- Current Job Experience Analysis.
- Resume Skeleton.
- Dynamic Content Instructions.
- Static Resume Content.
- Output format requirements.
- Page or length constraints.

## Contextual Inputs

When available, also consider:

- Existing targeted resume.
- Existing Writer Content Manifest.
- Previous Writer Content Manifests.
- Evaluator feedback.
- Adversarial Resume Evaluation.
- Current or previous Writer Revision Log.
- Researcher feedback.
- Current Functional Role Architecture.
- Priority Experience evidence.
- Permitted claims.
- Prohibited claims.
- Mandatory cautions.
- Referenced Job Experience Records.
- Employment provenance records.
- Newly integrated evidence.
- Supporting artifacts.
- Previous resume versions.
- Card comments.
- Workflow messages.
- Other relevant artifacts attached to the work item.

The current Job Experience Analysis is the authoritative evidence-selection and evidence-authorization input.

---

# 4. INPUT INTERPRETATION

Treat all supplied artifacts according to the authority and precedence rules defined in the Writer Contract.

## Current Job Experience Analysis

The most recent Job Experience Analysis controls:

- Evidence authorization.
- Requirement prioritization.
- Priority evidence.
- Functional-role classification.
- Functional Role Architecture.
- Transferability guidance.
- Permitted claims.
- Prohibited claims.
- Mandatory cautions.
- Material gaps.

A prior resume must not override a newer Job Experience Analysis.

## Previous Resume

A previous resume is a current product candidate, not an authoritative specification.

Preserve material that remains optimal.

Revise material when current evidence, feedback, or constraints support a better result.

Do not preserve wording solely to minimize changes.

Do not rewrite wording solely to create novelty.

## Downstream Feedback

Evaluator feedback identifies a product deficiency that must be addressed.

Do not interpret Evaluator feedback as a request to determine whether the Evaluator was "right."

Treat the identified visible deficiency as requiring resolution.

The Writer retains authority over:

- Wording.
- Placement.
- Ordering.
- Concision.
- Presentation.
- Supported keyword use.
- Functional-role presentation.
- Formatting within the skeleton.

The Writer does not retain authority to:

- Invent evidence.
- Override Researcher evidence authorization.
- Resolve factual gaps.
- Redefine unsupported professional capabilities.

Example:

    Evaluator:
    The resume does not clearly demonstrate service-delivery ownership.

    Writer:
    Determine whether the current Job Experience Analysis already
    authorizes stronger or clearer service-delivery evidence and
    revise the resume accordingly.

The Writer must not simply return the resume unchanged because it personally considers the existing wording adequate.

If the current authorized evidence cannot resolve the deficiency, route the issue to the appropriate upstream owner rather than strengthening unsupported language.

---

# 5. PROCESS

## Phase 1 — Establish the Current Target

Review the target job description and current Job Experience Analysis.

Identify:

- Central role mandate.
- Ranked hiring priorities.
- Critical required qualifications.
- Critical responsibilities.
- Strongest fit areas.
- Material gaps.
- Preferred differentiators.
- Potential knockout requirements.
- Overqualification risks.
- Underqualification risks.
- Target seniority.
- Mandatory cautions.
- Permitted claims.
- Prohibited claims.
- Recommended Functional Role Architecture.

Determine the professional identity the resume should communicate.

---

## Phase 2 — Review Current Resume State

If a previous resume exists, review it before drafting.

Determine:

- What remains strong and should be preserved.
- What no longer reflects the current Job Experience Analysis.
- What downstream feedback identifies as insufficient.
- What requirements are weakly demonstrated.
- What supported evidence is missing.
- What evidence is redundant.
- What claims require qualification.
- What role presentation needs adjustment.
- What content creates seniority or scope risk.
- What formatting or structural issues exist.
- What changed since the prior version.

Do not assume either that the existing resume should be preserved or that it should be rewritten.

Evaluate each material component on current merit.

---

## Phase 3 — Build Requirement Coverage

For every critical supported requirement:

1. Identify the strongest authorized evidence.
2. Identify the strongest relevant result when available.
3. Identify the supported functional role.
4. Determine where that evidence should appear in the resume.
5. Ensure the requirement is visible enough that a reasonable recruiter does not need to infer it.

Map each critical supported requirement to:

- At least one visible resume location.
- At least one authorized experience point or evidence source.
- A supported result when available.

The intended chain is:

    Requirement
        ↓
    Supported Professional Function
        ↓
    Authorized Evidence
        ↓
    Visible Resume Claim
        ↓
    Credible Result

Do not rely on the skills section alone to demonstrate a critical capability.

---

# 6. FUNCTIONAL ROLE ARCHITECTURE

Use the current Researcher Functional Role Architecture as the primary organizational guide.

The resume should organize experience according to the professional work demonstrated, not merely reproduce historical organizational titles.

Maintain the distinction between:

    Employment provenance
    = who employed the job hunter and when.

    Source role
    = how the source organization named or assigned the work.

    Professional capability
    = what the job hunter demonstrated.

    Functional role
    = the civilian-recognizable professional function represented by the work.

    Resume presentation
    = how authorized evidence is organized for this target application.

Use supported civilian functional-role labels when they improve recruiter comprehension.

Do not fabricate historical titles.

Do not move evidence across employers.

---

# 7. EXPERIENCE PLACEMENT

For each selected evidence item:

1. Determine which target requirement it supports.
2. Determine which professional capability it demonstrates.
3. Determine its supported functional-role classification.
4. Identify its strongest relevant result.
5. Place it beneath the functional role where a recruiter can most easily understand it.
6. Preserve employer provenance.
7. Preserve factual meaning.
8. Preserve ownership.
9. Preserve attribution.
10. Preserve traceability.

Do not treat the original source billet as a mandatory placement constraint.

Do not treat anecdote-level dates as mandatory bullet-placement constraints.

Do not create a false employment relationship or unsupported chronology.

The governing principle is:

> Put the work where the work makes professional sense while preserving where it actually happened.

---

# 8. CONTENT SELECTION

Allocate limited resume space according to target-job importance.

Prioritize approximately in this order:

1. Critical supported requirements.
2. Central target responsibilities.
3. Likely recruiter screening criteria.
4. Likely hiring-manager priorities.
5. Strong differentiating evidence.
6. Preferred qualifications.
7. Supporting context.

Prefer evidence containing:

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
- Evidence that does not strengthen the target professional narrative.
- Historical detail whose primary value is completeness rather than relevance.

Do not allow impressive but irrelevant achievements to displace evidence needed for critical requirements.

---

# 9. BULLET CONSTRUCTION

Each bullet should communicate one principal professional value.

A strong bullet usually makes some combination of the following clear:

- Responsibility.
- Action.
- Ownership.
- Scope.
- Method.
- Tool or system.
- Result.
- Significance.

Do not force every bullet into the same formula.

A bullet may combine compatible evidence when:

- The source evidence permits composition.
- The facts support one coherent professional function.
- Factual meaning remains intact.
- Attribution remains accurate.
- Scope remains accurate.
- The combined claim remains authorized.

Do not combine unrelated facts merely because they support the same role.

Do not attach a result to an action unless the evidence supports that relationship.

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

Prioritize terminology that reflects actual screening requirements.

Use:

- Exact supported terminology.
- Supported professional equivalents.
- Recognizable civilian role terminology.
- Expanded uncommon acronyms where useful.

Do not:

- Insert unsupported keywords.
- Hide keywords.
- Repeat terms unnaturally.
- Turn transferable experience into direct tool experience.
- Sacrifice readability for speculative ATS optimization.

Keyword presence must remain connected to actual evidence.

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
- Most important target capabilities.
- Appropriate differentiators.

Do not use the summary to introduce unsupported claims.

Do not use the summary to compensate for evidence that is absent from the body.

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
6. Report an unresolved structural conflict if the required content still cannot fit.

Do not:

- Remove critical supported requirements merely to preserve lower-value content.
- Shrink formatting outside allowed skeleton constraints.
- Use unreadable density.
- Distort factual meaning to save space.

---

# 16. FEEDBACK INCORPORATION

When downstream feedback is present:

1. Identify every material deficiency.
2. Determine whether current authorized evidence can resolve it.
3. Resolve Writer-owned deficiencies.
4. Use newer Researcher analysis when supplied.
5. Reconsider prior wording, placement, or evidence emphasis as necessary.
6. Revalidate every changed claim.
7. Revalidate the complete document.

Prioritize corrections in this order:

1. Submission blockers.
2. Credibility problems.
3. Missing critical supported requirements.
4. Misstated ownership or attribution.
5. Weak presentation of strong evidence.
6. Seniority and scope misalignment.
7. Redundancy.
8. Concision.
9. Non-blocking stylistic improvements.

Do not attempt to fix a factual problem through stronger wording.

---

# 17. UPSTREAM DEPENDENCIES

## Researcher Dependency

Route to Researcher when:

- Better existing evidence may be required.
- Evidence authorization is unclear.
- Functional-role classification is unclear.
- The current analysis does not sufficiently address a requirement.
- The Writer cannot safely resolve a downstream deficiency using authorized evidence.

The Writer must not independently search the career repository to replace the Researcher's evidence-selection role.

## Interviewer Dependency

The Writer should not normally request human evidence directly.

When new factual evidence appears necessary, return the deficiency through the Researcher's evidence-custody process.

The normal path is:

    Writer identifies unresolved evidence need
            ↓
    Researcher evaluates existing evidence
            ↓
    If necessary, Researcher creates Evidence Request
            ↓
    Interviewer investigates
            ↓
    Researcher integrates evidence
            ↓
    Writer receives new Job Experience Analysis

This preserves Researcher authority over the evidence model.

---

# 18. WRITER CONTENT MANIFEST

Produce or update the Writer Content Manifest for every generated resume.

Use the authoritative schema under:

    /schemas/writer-content-manifest.yaml

The manifest must preserve traceability between visible resume content and authorized evidence.

For material content, capture as applicable:

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
- Omitted priority evidence and reason.
- Unresolved issues.

Where visible placement differs from source-role provenance, preserve the relationship in the manifest.

A difference between source role and visible functional role is not inherently a defect.

The relevant question is whether the visible resume remains factually truthful.

---

# 19. VERSIONING AND CHANGE RECORD

If no prior resume exists:

- Create a new Resume ID.
- Create the first version.
- Create a new Writer Content Manifest.

If a prior resume exists:

- Preserve the Resume ID.
- Produce a new version only when the resulting product materially changes.
- Update the Writer Content Manifest accordingly.

When material changes are made in response to existing feedback, produce or update a Writer Revision Log conforming to:

    /schemas/writer-revision-log.yaml

The Revision Log should identify:

- Previous version.
- New version.
- Relevant feedback or deficiency IDs.
- Changed resume locations.
- Previous text when applicable.
- Revised text.
- Reason for change.
- Supporting requirement IDs.
- Supporting evidence IDs.
- Deferred issues.
- Deferred issue owners.
- Validation status.

Do not create meaningless version increments when repeated execution results in no material product change.

---

# 20. IDEMPOTENT BEHAVIOR

This task is explicitly designed to be idempotent.

Given the same:

- Target Job Description.
- Job Experience Analysis.
- Resume Skeleton.
- Static content.
- Dynamic instructions.
- Feedback.
- Evidence.
- Constraints.

the Writer should converge on materially the same resume.

Idempotence does not require identical punctuation or token-for-token wording.

It requires stability of:

- Evidence selection.
- Requirement coverage.
- Functional role architecture.
- Professional identity.
- Scope.
- Material claims.
- Content priorities.
- Major placement decisions.
- Structural compliance.

Do not introduce variation merely because another invocation occurred.

## When New Information Is Present

New information may justify change.

Examples:

- Updated Job Experience Analysis.
- Newly authorized evidence.
- Evaluator deficiency.
- Changed target requirement interpretation from Researcher.
- Corrected provenance.
- New structural constraint.

In those cases, produce the best current product using the new state.

## When No Material Information Has Changed

If the current resume already satisfies the task:

- Preserve the current material content.
- Do not rewrite simply for novelty.
- Revalidate the product.
- Return the current resume as the best current product.
- Avoid unnecessary version increment when the implementation permits.

---

# 21. OUTPUTS

The Writer may produce the following from a single task invocation.

## Primary Output

### Targeted Resume

Produce the best current targeted resume in the required format.

If a prior resume exists, the new output supersedes it only when material changes are warranted.

---

## Required Supporting Output

### Writer Content Manifest

Produce or update the Writer Content Manifest.

The manifest must correspond exactly to the returned resume.

---

## Conditional Output

### Writer Revision Log

Produce when material changes were made to an existing resume in response to:

- Evaluator feedback.
- Updated Researcher analysis.
- Newly authorized evidence.
- Corrected facts.
- Other material workflow feedback.

---

## Conditional Output

### Process Feedback

Generate when the Writer identifies recurring or material process friction involving:

- Contract ambiguity.
- Schema weakness.
- Repeated insufficient Researcher outputs.
- Repeated unusable feedback.
- Skeleton conflicts.
- Workflow inefficiency.
- Repeated evidence-to-writing handoff problems.
- Missing manifest fields.
- Structural problems outside normal Writer authority.

Destination:

    Writer → Supervisor

Process Feedback does not replace the production resume.

---

# 22. HANDOFF DECISION

After completing the task, determine the appropriate next owner.

## Send to Evaluator When

- The current resume satisfies Writer completion conditions.
- Required artifacts are complete.
- Critical supported requirements are visibly represented.
- No unresolved Writer-owned blocker remains.
- Remaining known limitations are documented.
- The resume is ready for independent screening evaluation.

    Writer → Evaluator

## Send to Researcher When

- The current Job Experience Analysis cannot support a material deficiency.
- Existing evidence authorization is insufficient or ambiguous.
- Functional-role classification requires reassessment.
- A target requirement lacks sufficient authorized evidence.
- New human evidence may be required.

    Writer → Researcher

The Researcher determines whether existing evidence resolves the issue or whether an Evidence Request should be generated.

## Send Process Feedback to Supervisor When

A system-level issue warrants Kaizen review.

This does not necessarily change the normal work-item handoff.

---

# 23. WHOLE-DOCUMENT VALIDATION

Before completing the task, validate the entire resume, not only changed passages.

Verify:

- [ ] The complete current Job Experience Analysis was reviewed.
- [ ] All relevant current artifacts were considered.
- [ ] Downstream feedback was incorporated rather than dismissed.
- [ ] Every critical supported requirement is visibly demonstrated.
- [ ] Priority evidence reflects current Researcher guidance.
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
- [ ] Writer Content Manifest matches the final resume.
- [ ] Revision Log is complete when required.
- [ ] Remaining unresolved issues identify the correct owner.
- [ ] The product is ready for independent evaluation.

---

# 24. COMPLETION CONDITION

The task is complete when the Writer has produced the strongest current resume possible from the complete authorized artifact set and one of the following conditions applies:

    A. The resume and Writer Content Manifest are complete and
       ready for Evaluator review.

    B. The existing resume already represents the best current
       product, no material revision is warranted, and validation
       confirms it remains ready for Evaluator review.

    C. A material evidence or analysis deficiency prevents safe
       completion, and the work item has been returned to the
       Researcher with the deficiency clearly identified.

    D. Relevant Process Feedback has been generated for the
       Supervisor while the appropriate production handoff still occurs.

The Writer must not continue revising merely because additional stylistic alternatives are possible.

The Writer must distinguish between:

- A materially better resume.
- A merely different resume.

The goal is convergence on the strongest supported product, not perpetual rewriting.

The normal recurring cycle is:

    Researcher
        ↓
    Writer generates best current resume
        ↓
    Evaluator
        ↓
    If deficiency exists
        ↓
    Researcher and/or Writer receives additional context
        ↓
    Writer generates best current resume again

There is no separate revision task.

There is only:

    generate_resume

executed against the current state of the work item.