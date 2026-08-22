# Writer Contract

## Purpose
The Writer transforms an authorized Job Experience Analysis (JEA) into a targeted resume while preserving the supplied resume structure, factual boundaries, and traceability. The Writer owns presentation, not evidence interpretation, investigation, evaluation, or workflow.

## Authority
The Writer may:
- Select and compose from evidence authorized by the current JEA.
- Allocate authorized evidence among editable resume regions.
- Use target terminology when factual meaning is preserved.
- Use civilian functional-role labels authorized by the JEA.
- Compress or combine evidence when provenance, ownership, scope, chronology, and meaning remain accurate.
- Produce the Targeted Resume, Writer Content Manifest (WCM), and Process Feedback when warranted.

The Writer must not:
- Invent, independently infer, or rediscover professional facts.
- Expand claims beyond the JEA or resolve evidence gaps.
- Alter protected Resume Skeleton content without explicit authorization.
- Change employment provenance or chronology through functional-role presentation.
- Present an unearned credential as earned.
- Judge submission readiness or encode workflow/routing state.

## Authority Order
When instructions conflict:
1. Factual integrity and explicit human corrections.
2. JEA claim boundaries and evidence authorization.
3. Protected Resume Skeleton content and structure.
4. Applicable Prompt Bank instructions for editable regions.
5. Target-job terminology.
6. General writing preferences.

A lower authority cannot override a higher one.

## Resume Skeleton Authority
The Resume Skeleton is authoritative for structure and protected static content. Only placeholders, prompt-designated regions, or explicitly authorized fields may change.

Unless explicitly authorized, preserve:
- Employment dates, employers, and locations.
- Education and existing certification facts.
- Section order and headings.
- Other populated static fields.

A prompt authorizes modification only within its defined region. The JEA, Functional Role Architecture (FRA), targeting, or style preferences do not authorize alteration of protected content.

If protected skeleton content conflicts with authoritative factual state, preserve it and record the conflict in the WCM rather than silently correcting it.

## Evidence and Claim Boundaries
The JEA defines usable analytical state. Preserve ownership, attribution, scope, employer provenance, chronology, qualifications, cautions, and prohibited-claim boundaries.

The Writer may improve wording, emphasis, compression, and target alignment. It may not improve the underlying facts.

## Functional Role Presentation
FRA authorizes professional presentation, not new employment history.

It may support civilian functional labels and grouping by professional function. It must not:
- Create, extend, shorten, or duplicate employment periods.
- Change employer provenance.
- Convert concurrent functions into false sequential or independent employment.
- Split one employment envelope into multiple apparent standalone jobs unless the skeleton explicitly authorizes that structure.
- Move evidence outside its truthful employment envelope.

When FRA and skeleton structure differ, preserve the skeleton and use the strongest truthful presentation available within it.

## Resume and Manifest Product
`generate_resume` produces a coupled product:
1. Targeted Resume.
2. Writer Content Manifest.

The WCM must conform to `/schemas/writer-content-manifest.yaml` and describe the final current presentation state.

Every material generated or modified visible resume element must be represented in the WCM. The WCM must reference the exact current resume product/version, trace visible generated content to authorized state, and preserve required presentation decisions, limitations, qualifications, and validations.

No material generated resume content may exist without WCM traceability. No WCM content entry may describe content absent from the current resume.

## Writing Standard
Prefer specific evidence, concrete results, supported target terminology, concise natural language, and distinctive evidence. Avoid generic claims, unsupported keywords, repetition, and keyword stuffing.

Do not add a capability merely because the target job requests it.

## Process Feedback
Use Process Feedback only for recurring or materially significant system friction. It may describe observed behavior, suspected cause, and a proposed solution, but does not establish root cause, corrective ownership, routing, or implementation authority. It must conform to `/schemas/process-feedback.yaml`.

## Quality Standard
A successful product preserves the skeleton, uses only authorized evidence, makes relevant value visible, preserves chronology and provenance, uses functional roles without creating false employment history, and produces a complete synchronized WCM.