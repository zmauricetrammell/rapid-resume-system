# WRITER TASK INSTRUCTION — GENERATE COVER LETTER

**Task Version:** 2.0  
**Task ID:** generate_cover_letter  
**Agent:** Writer  
**System:** Rapid Resume System

---

# 1. TASK

Generate the best current targeted cover letter from all available artifacts.

This task produces a concise cover letter that connects the job hunter's strongest supported experience to the employer's most important needs without merely repeating the resume.

The same task is used whether:

- No previous cover letter exists.
- A previous cover letter already exists.
- A newer Job Experience Analysis has been supplied.
- A newer targeted resume has been supplied.
- New evidence has been integrated by the Researcher.
- Feedback concerning the cover letter has been supplied.
- Personalization information has been added.
- The work item has returned to the Writer multiple times.

Do not treat initial generation and revision as separate task types.

Each invocation must evaluate the complete current artifact set and produce the strongest current cover letter supported by the available evidence and constraints.

The task is idempotent in intent:

> Given the same authoritative inputs and constraints, repeated execution should converge on materially the same cover letter rather than producing unnecessary variation.

---

# 2. OBJECTIVE

Create a concise, credible, targeted cover letter that explains why the job hunter's strongest supported experience is relevant to the employer's most important needs.

The cover letter should:

1. Establish the target professional identity.
2. Connect the candidate to the employer's central mandate.
3. Highlight two or three of the most important supported hiring priorities.
4. Use a small number of complementary professional examples.
5. Explain why those examples matter for the target role.
6. Add narrative value beyond the resume.
7. Remain fully supported by the current evidence.
8. Avoid unnecessary repetition.
9. Preserve factual integrity and traceability.
10. Follow the supplied cover-letter structure and formatting requirements.

The cover letter is not a career summary.

It is a focused argument connecting:

    Employer Need
        ↓
    Candidate Capability
        ↓
    Supporting Experience
        ↓
    Relevant Result
        ↓
    Value to Target Role

---

# 3. INPUT MODEL

The Writer must consider **all relevant artifacts supplied with the work item**.

The presence of additional artifacts does not create a different task.

It changes the available context.

## Minimum Required Inputs

- Target Job Description.
- Current Job Experience Analysis.
- Cover-Letter Skeleton or approved structural instructions.
- Output format and length requirements.

## Contextual Inputs

When available, also consider:

- Current targeted resume.
- Writer Content Manifest.
- Previous cover letter.
- Previous cover-letter feedback.
- Current Functional Role Architecture.
- Priority Experience evidence.
- Permitted claims.
- Prohibited claims.
- Mandatory cautions.
- Referenced Job Experience Records.
- Employer-provided information.
- Job-hunter-provided motivation.
- Job-hunter-provided employer knowledge.
- Hiring-manager name.
- Recruiter name.
- Referral information.
- Relevant networking context.
- Employment provenance.
- Supporting source materials.
- Card comments.
- Workflow messages.
- Other relevant artifacts attached to the work item.

The current Job Experience Analysis is the authoritative evidence-selection and evidence-authorization input.

---

# 4. INPUT INTERPRETATION

Treat all supplied artifacts according to the authority and precedence rules defined in the Writer Contract.

## Job Experience Analysis

The most recent Job Experience Analysis controls:

- Target priorities.
- Evidence authorization.
- Priority evidence.
- Functional-role classifications.
- Permitted claims.
- Prohibited claims.
- Material gaps.
- Mandatory cautions.
- Target seniority.
- Professional positioning.

Do not introduce a claim merely because it appears in an older cover letter or resume if it is not supported by the current analysis.

## Targeted Resume

The targeted resume is useful for:

- Maintaining professional consistency.
- Avoiding unnecessary repetition.
- Understanding which evidence is already prominently visible.
- Identifying opportunities for complementary narrative.

The cover letter must not simply paraphrase the resume.

## Previous Cover Letter

A previous cover letter is a current product candidate, not an authoritative specification.

Preserve material that remains optimal.

Change material when newer evidence, feedback, personalization, or constraints support a better result.

Do not rewrite simply for novelty.

---

# 5. PERSONALIZATION AUTHORITY

The Writer must distinguish between evidence-backed professional content and personalization.

## The Writer May Use

Personalization explicitly supplied through approved artifacts, including:

- Employer name.
- Target role.
- Hiring-manager or recruiter name.
- Referral information.
- Confirmed networking interactions.
- Job-hunter-provided reasons for interest.
- Job-hunter-provided knowledge of the organization.
- Confirmed geographic or personal connection when relevant.
- Employer information contained in supplied materials.

## The Writer Must Not Invent

- Personal enthusiasm.
- Emotional attachment to the employer.
- Long-standing interest in the company.
- Knowledge of company culture not supported by supplied information.
- Personal connection to the mission.
- Referral relationships.
- Conversations that did not occur.
- Employer facts not present in approved source material.
- Motivation the job hunter did not express.

If personalization information is unavailable, write a strong professional letter without fabricated enthusiasm.

A credible professional connection is preferable to invented passion.

---

# 6. PROCESS

## Phase 1 — Establish the Employer Need

Review the Target Job Description and current Job Experience Analysis.

Identify:

- Employer's central mandate for the role.
- Two or three highest-priority supported hiring needs.
- Critical capabilities.
- Key challenges or responsibilities.
- Target seniority.
- Strongest candidate fit areas.
- Material cautions or gaps.

Do not attempt to address every requirement.

The cover letter should focus on the few capabilities most useful for making the candidate's fit understandable.

---

## Phase 2 — Review the Current Application Narrative

Review the current targeted resume when available.

Identify:

- Professional identity already established.
- Strongest experiences already visible.
- Most important achievements.
- Evidence heavily emphasized in the resume.
- Important evidence that could benefit from additional narrative context.
- Themes that connect several experiences.
- Areas where the cover letter can add meaning rather than repetition.

The cover letter and resume should reinforce the same professional identity.

They should not compete with or contradict one another.

---

## Phase 3 — Select Evidence

Select a small number of complementary evidence examples.

Prefer examples that collectively demonstrate:

- Direct relevance to the employer's priorities.
- Clear ownership.
- Appropriate scope.
- Strong professional judgment.
- Credible results.
- Different but complementary dimensions of fit.

Avoid selecting multiple examples that all prove essentially the same thing unless that capability is exceptionally central to the target role.

Use only claims authorized by the current Job Experience Analysis.

---

# 7. NARRATIVE STRATEGY

The cover letter should explain relationships the resume cannot efficiently explain.

Useful narrative functions include:

- Connecting experiences from different roles into one professional theme.
- Explaining how technical depth supports management capability.
- Explaining how management experience strengthens technical leadership.
- Connecting transformation work to the employer's current needs.
- Showing progression or breadth without narrating the whole career.
- Explaining why a particular accomplishment is relevant to this job.
- Highlighting the interaction between several capabilities.
- Establishing a professional identity that is more coherent than source organizational titles suggest.

The cover letter should answer:

> Why are these experiences especially relevant to what this employer needs?

It should not answer merely:

> What has this person done?

The resume already performs much of that function.

---

# 8. STRUCTURE

Follow the supplied cover-letter skeleton when one exists.

Unless the approved skeleton specifies otherwise, the conceptual structure should be:

## Opening

Establish:

- Target role.
- Professional identity.
- Central connection between candidate capability and employer need.

Avoid generic openings such as:

    "I am writing to express my interest in..."

when a more substantive opening is possible.

Do not invent enthusiasm to make the opening sound personal.

## Evidence Paragraph 1

Connect one major employer priority to a strong supported professional example.

Explain:

- Relevant responsibility.
- Candidate contribution.
- Meaningful scope.
- Result.
- Why it matters to the target role.

## Evidence Paragraph 2

Use a complementary example or professional theme.

Demonstrate another important dimension of fit.

Avoid repeating the first paragraph with different nouns.

## Closing

Briefly reinforce:

- Overall fit.
- Professional value.
- Any authorized genuine interest or connection.

Close professionally.

Do not introduce new evidence in the final paragraph.

---

# 9. EVIDENCE-TO-NEED CONNECTION

For each major example used in the letter, establish:

    Employer Priority
        ↓
    Candidate Capability
        ↓
    Confirmed Professional Example
        ↓
    Credible Result
        ↓
    Relevance to Target Role

Do not merely state an accomplishment and expect the reader to infer its relevance.

Explain the professional connection directly.

For example, prefer the structure:

    The employer needs reliable service operations.

    The candidate led service-delivery improvement at meaningful scale.

    The work materially reduced resolution time.

    That experience demonstrates the operational leadership
    directly relevant to the target role.

The final prose should be natural rather than mechanically following this sequence.

---

# 10. RELATIONSHIP TO THE RESUME

The cover letter must complement the resume.

Do not:

- Repeat resume bullets verbatim.
- List every major accomplishment.
- Restate the professional summary.
- Reproduce the core-skills section.
- Walk through the resume chronologically.
- Summarize the entire career.

Instead:

- Select a few examples.
- Add context.
- Explain significance.
- Connect examples across roles.
- Clarify professional themes.
- Make target relevance explicit.

A reader who reviews both documents should gain additional understanding from the cover letter.

---

# 11. PROFESSIONAL TRANSLATION

Apply the same professional-translation principles used in the resume.

Use civilian-recognizable terminology when supported.

Preserve the distinction between:

    Employment provenance
    = where the work occurred.

    Source role
    = how the source organization named the work.

    Professional capability
    = what the job hunter demonstrated.

    Functional role
    = the civilian-recognizable function represented by the work.

Do not force unfamiliar military or internal terminology into the letter when an accurate civilian translation exists.

Do not fabricate historical titles.

Do not change employer provenance.

---

# 12. WRITING STYLE

Write concise, natural, professional prose.

Prefer:

- Specific professional language.
- Clear relationships between evidence and employer needs.
- Varied sentence structure.
- Concrete examples.
- Appropriate confidence.
- Direct statements.
- Specific qualitative or quantitative outcomes.

Avoid:

- Generic praise of the employer.
- Excessive flattery.
- Unsupported enthusiasm.
- Empty adjectives.
- Corporate clichés.
- Repetition of job-description wording.
- Mechanical paragraph formulas.
- Excessive em dashes.
- Unnecessary three-part lists.
- Resume-style bullet language inside prose.
- Overly formal or ceremonial language.
- Long autobiographical background.
- Unnecessary explanations of military or organizational structure.

The letter should sound like a capable professional explaining why their experience matters.

---

# 13. FACTUAL INTEGRITY

Every material professional claim must be authorized by the current Job Experience Analysis.

Preserve:

- Responsibility.
- Ownership.
- Scope.
- Attribution.
- Proficiency.
- Tool or system accuracy.
- Results.
- Qualifications.
- Evidence limitations.

Do not:

- Invent metrics.
- Broaden ownership.
- Increase scope.
- Convert transferable experience into direct experience.
- Attribute team results solely to the job hunter.
- Add unsupported employer knowledge.
- Create personal motivations.
- Resolve evidence gaps through persuasive language.

Persuasion must come from selecting and explaining strong evidence, not from strengthening the facts.

---

# 14. GAP HANDLING

Do not disguise genuine experience gaps.

If the Job Experience Analysis identifies a material gap:

- Do not claim the missing experience.
- Do not imply direct experience through ambiguous wording.
- Do not use the cover letter to compensate with unsupported equivalence.

When appropriate, emphasize complementary supported strengths.

If the missing evidence materially prevents the Writer from producing a credible letter, return the deficiency through the Researcher's evidence-custody process.

Normal path:

    Writer identifies evidence deficiency
            ↓
    Researcher evaluates current evidence
            ↓
    If necessary, Researcher creates Evidence Request
            ↓
    Interviewer investigates
            ↓
    Researcher integrates evidence
            ↓
    Writer generates cover letter again

---

# 15. PERSONALIZATION GAPS

If a cover-letter requirement calls for information not currently available, identify it as a personalization gap.

Examples:

- Hiring-manager name.
- Referral relationship.
- Specific motivation for employer.
- Authorized knowledge of company mission.
- Geographic connection.
- Prior interaction with the organization.

Classify whether the gap is:

- Required.
- Useful but optional.
- Not material.

Do not block an otherwise strong cover letter solely because optional personalization is unavailable.

Do not fabricate personalization to eliminate the gap.

---

# 16. LENGTH AND FORMAT

Follow the supplied cover-letter skeleton, length, salutation, and formatting requirements.

Unless a supplied standard requires otherwise:

- Prefer concise presentation.
- Avoid unnecessary repetition.
- Use sufficient detail to establish evidence and relevance.
- Preserve readability.
- Keep the document focused on the target role.

When content exceeds available space, reduce in this order:

1. Redundant explanation.
2. Lower-priority evidence.
3. Secondary context.
4. Repetitive employer language.
5. Nonessential personalization.

Do not remove the core evidence-to-need connection merely to preserve decorative language.

---

# 17. WRITER CONTENT MANIFEST

Produce or update a Writer Content Manifest for the cover letter.

Use the authoritative schema under:

    /schemas/writer-content-manifest.yaml

The manifest should identify, as applicable:

- Cover-letter content ID.
- Paragraph or location.
- Final text.
- Requirement IDs.
- Experience-point IDs.
- Result IDs.
- Evidence references.
- Functional-role relationship.
- Terminology normalization.
- Personalization source.
- Attribution validation.
- Scope validation.
- Prohibited-claim validation.
- Unresolved personalization gaps.

Every material professional claim must remain traceable.

If the existing Writer Content Manifest schema cannot represent both resume and cover-letter content cleanly, generate Process Feedback for the Supervisor rather than silently redefining the schema.

---

# 18. IDEMPOTENT BEHAVIOR

This task is explicitly designed to be idempotent.

Given the same:

- Target Job Description.
- Job Experience Analysis.
- Targeted Resume.
- Cover-Letter Skeleton.
- Personalization artifacts.
- Feedback.
- Evidence.
- Constraints.

the Writer should converge on materially the same cover letter.

Idempotence does not require identical token-for-token wording.

It requires stability of:

- Employer priorities selected.
- Evidence examples selected.
- Professional identity.
- Material claims.
- Narrative strategy.
- Personalization.
- Major paragraph functions.
- Factual scope.
- Overall positioning.

Do not introduce variation merely because another invocation occurred.

## When New Information Is Present

New information may justify change.

Examples:

- Updated Job Experience Analysis.
- New authorized evidence.
- Updated resume positioning.
- New personalization information.
- Corrected facts.
- Material feedback.
- New formatting constraint.

Use the new state to produce the best current cover letter.

## When No Material Information Has Changed

If the existing cover letter already satisfies the task:

- Preserve the current material content.
- Do not rewrite for novelty.
- Revalidate it.
- Return it as the best current product.
- Avoid unnecessary version increments where implementation permits.

---

# 19. OUTPUTS

## Primary Output

### Targeted Cover Letter

Produce the best current targeted cover letter in the required format.

---

## Required Supporting Output

### Writer Content Manifest

Produce or update the Writer Content Manifest corresponding to the returned cover letter.

---

## Conditional Output

### Personalization Gaps

Identify unresolved personalization gaps when relevant.

For each gap, state:

- Missing information.
- Whether it is required or optional.
- Impact on the current letter.
- Appropriate owner.

Do not invent missing information.

---

## Conditional Output

### Process Feedback

Generate when the Writer identifies recurring or material system friction involving:

- Cover-letter skeleton weakness.
- Schema limitations.
- Repeated missing personalization fields.
- Contract ambiguity.
- Evidence handoff problems.
- Redundant task requirements.
- Workflow inefficiency.
- Repeated conflict between resume and cover-letter requirements.

Destination:

    Writer → Supervisor

Process Feedback does not replace the cover-letter output.

---

# 20. HANDOFF DECISION

After generating the cover letter, determine the appropriate next owner.

## Complete the Writer Stage When

- The cover letter satisfies its completion conditions.
- The Writer Content Manifest is complete.
- No material Writer-owned blocker remains.
- Known personalization gaps are documented.
- The document is ready for the next approved workflow stage.

## Send to Researcher When

- Current evidence authorization cannot support a material claim needed for the letter.
- Target-role analysis is insufficient to establish the intended narrative.
- A material evidence deficiency exists.

    Writer → Researcher

The Researcher determines whether existing evidence resolves the problem or whether new human evidence should be requested.

## Send Process Feedback to Supervisor When

A system-level issue warrants Kaizen review.

This does not necessarily alter the normal production handoff.

---

# 21. VALIDATION

Before completing the task, verify:

- [ ] The current Target Job Description was reviewed.
- [ ] The current Job Experience Analysis was reviewed.
- [ ] The current targeted resume was reviewed when available.
- [ ] The employer's central mandate is understood.
- [ ] Two or three important supported priorities were selected.
- [ ] Evidence examples are complementary rather than redundant.
- [ ] Every material professional claim is authorized.
- [ ] The letter explains why selected evidence matters to the target role.
- [ ] The letter does not summarize the entire career.
- [ ] Resume bullets are not repeated verbatim.
- [ ] Professional identity is consistent with the resume.
- [ ] Functional translation remains accurate.
- [ ] Employer provenance is preserved.
- [ ] Ownership is preserved.
- [ ] Scope is preserved.
- [ ] Attribution is preserved.
- [ ] Unsupported claims are absent.
- [ ] Unsupported enthusiasm is absent.
- [ ] Unsupported employer knowledge is absent.
- [ ] Unsupported personal motivation is absent.
- [ ] Material gaps are not disguised.
- [ ] Personalization gaps are disclosed when relevant.
- [ ] The supplied skeleton and formatting requirements are satisfied.
- [ ] Length constraints are satisfied.
- [ ] Language is natural and non-formulaic.
- [ ] Writer Content Manifest matches the final document.
- [ ] Every material claim remains traceable.
- [ ] The resulting letter adds value beyond the resume.

---

# 22. COMPLETION CONDITION

The task is complete when the Writer has produced the strongest current cover letter possible from the complete authorized artifact set and one of the following applies:

    A. The cover letter and Writer Content Manifest are complete
       and ready for the next workflow stage.

    B. The existing cover letter already represents the best
       current product, no material revision is warranted, and
       validation confirms it remains suitable.

    C. A material evidence or analysis deficiency prevents safe
       completion, and the work item has been returned to the
       Researcher with the deficiency identified.

    D. Optional personalization remains unavailable, the gap has
       been documented, and the cover letter remains otherwise
       complete.

    E. Relevant Process Feedback has been generated for the
       Supervisor while the appropriate production handoff still occurs.

The Writer must not continue rewriting merely because stylistic alternatives remain possible.

The Writer must distinguish between:

- A materially better cover letter.
- A merely different cover letter.

The goal is convergence on the strongest supported narrative.

There is no separate revision task.

There is only:

    generate_cover_letter

executed against the current state of the work item.