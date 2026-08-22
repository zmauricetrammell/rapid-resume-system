# Task: Generate Resume

## Purpose
Produce the strongest truthful targeted resume permitted by the current JEA while preserving the Resume Skeleton and creating a complete WCM.

## Artifact Contract
This task produces two coupled outputs:
1. Targeted Resume.
2. Writer Content Manifest.

Authoritative WCM schema:

    /schemas/writer-content-manifest.yaml

Schema conformance is mandatory. Resume and WCM must describe the same final product state.

## Required Inputs
- Target Job Description.
- Current JEA.
- Resume Skeleton.
- Applicable Prompt Bank or dynamic content instructions.
- `/schemas/writer-content-manifest.yaml`.

Use applicable product feedback only when supplied as authorized input. Do not independently rediscover professional evidence.

## Method

### 1. Establish the Editable Surface
Before writing, distinguish protected skeleton content from editable prompt-designated content.

Preserve protected content exactly unless explicit authority permits modification. Protected content includes populated dates, employers, locations, education facts, certification facts, headings, section order, and other static fields not designated for generation.

A placeholder or prompt authorizes changes only within its defined region.

### 2. Read the Analytical State
Use the JEA to identify target requirements, priority evidence, FRA, supported and prohibited claims, cautions, limitations, and presentation value. Do not exceed those boundaries.

### 3. Plan Evidence Placement
Choose authorized evidence that best supports the target while fitting the skeleton. Prefer relevant, concrete, quantified, distinctive evidence useful to the intended functional role.

Avoid repetitive evidence. Do not omit distinctive evidence that the JEA identifies as materially useful merely because another item satisfies the same requirement.

### 4. Apply Functional Role Architecture
Use authorized civilian functional labels and groupings only within skeleton-permitted structure.

FRA changes presentation, not history. Do not invent or change dates, duplicate one employment period across apparent standalone jobs unless the skeleton explicitly provides that structure, change employers, or turn concurrent functions into false sequential roles.

### 5. Write Editable Regions
Execute each applicable prompt only within its designated region.

Preserve factual ownership, scope, attribution, and qualifications. Prefer measurable results when authorized. Use target terminology only when factually equivalent.

For summaries and skills, include only demonstrated JEA-authorized capability.

For credentials, preserve exact earned status. Never convert candidacy, study, or planned certification into an earned credential.

### 6. Build the WCM
Create WCM entries as final resume content is established.

Every material generated or modified visible element must be traceable. The WCM must correspond to the exact final resume ID, version, and file reference and contain the schema-required evidence, role-presentation, composition, terminology, keyword, qualification, limitation, omission, decision, and validation state.

Static skeleton content need not be treated as Writer-generated evidence unless required by schema/task, but any static content materially altered by the Writer becomes generated/modified content and must be traced.

### 7. Validate the Final Coupled Product
Validate only after all writing, editing, and formatting changes are complete. Any later resume change requires the WCM to be synchronized before completion.

## Completion Validation

### Skeleton Integrity
- [ ] Only authorized editable regions changed.
- [ ] Protected dates, employers, locations, education, credentials, headings, and section order are unchanged.
- [ ] No targeting decision silently altered protected skeleton content.

### Factual Integrity
- [ ] Every generated factual claim is JEA-authorized.
- [ ] Ownership, scope, attribution, qualifications, and prohibited-claim boundaries are preserved.
- [ ] No unsupported credential or capability is implied.

### Chronology and Functional Roles
- [ ] Employer provenance and chronology remain truthful.
- [ ] No employment period was created or duplicated without explicit skeleton authority.
- [ ] Concurrent functions were not presented as false independent employment.

### Resume–Manifest Integrity
- [ ] WCM conforms to `/schemas/writer-content-manifest.yaml`.
- [ ] Every material generated/modified visible element has a WCM entry.
- [ ] Every WCM entry corresponds to final visible content.
- [ ] WCM references the exact current resume ID, version, and file.
- [ ] Evidence references use correct artifact versions.
- [ ] Resume and WCM represent the same final state.

### Presentation Quality
- [ ] Material requirements receive appropriate visible emphasis.
- [ ] Distinctive authorized evidence is preserved when materially useful.
- [ ] Content is concise and non-redundant.
- [ ] Target terminology is supported.
- [ ] Formatting and page limits follow the skeleton and prompts.

## Output
Return:
1. Completed Targeted Resume in the required format.
2. Schema-conformant Writer Content Manifest.

A short completion note may accompany them but does not replace either artifact.