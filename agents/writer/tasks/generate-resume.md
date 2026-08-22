# Task: Generate Resume

## Purpose
Produce the strongest truthful targeted resume permitted by the current JEA while preserving the Resume Skeleton, using the available page budget effectively, and creating a complete WCM.

## Artifact Contract
This task produces:
1. Targeted Resume.
2. Writer Content Manifest.

Authoritative WCM schema: `/schemas/writer-content-manifest.yaml`.

Schema conformance is mandatory. Resume and WCM must describe the same final product state.

## Required Inputs
- Target Job Description.
- Current JEA.
- Resume Skeleton.
- Applicable Prompt Bank or dynamic content instructions.
- WCM schema.

Do not independently rediscover professional evidence.

## Method
### 1. Establish the Editable Surface
Distinguish protected skeleton content from editable prompt-designated content. Preserve protected populated dates, employers, locations, education, certifications, headings, section order, and other static fields unless explicitly authorized.

### 2. Read the JEA
Identify requirements, priority evidence, FRA, supported/prohibited claims, cautions, limitations, and presentation value. Do not exceed those boundaries.

### 3. Plan and Write
Place the strongest authorized evidence within the skeleton. Prefer relevant, concrete, quantified, distinctive evidence. Avoid repetition. Execute prompts only within their designated regions. Preserve ownership, scope, attribution, chronology, and exact credential status.

FRA changes presentation, not history.

### 4. Optimize Page Utilization
After a complete factual draft, inspect the rendered document.

If substantial usable space remains:
1. Revisit JEA Priority Evidence and FRA.
2. Identify authorized evidence not yet presented.
3. Rank it by relevance, differentiation, result strength, scale, and contribution to role credibility.
4. Add the strongest non-redundant evidence.
5. Render and reassess.

Continue until the page budget is used effectively, no additional evidence would materially improve the resume, or further content would materially reduce readability.

For substantive roles, prefer at least three strong result bullets when evidence and space permit. Do not stop merely because every requirement already has some coverage.

### 5. Build and Synchronize the WCM
Trace every material generated or modified visible element. Protected static skeleton content does not require traceability unless modified. The WCM must identify the exact final resume product state.

### 6. Validate
- [ ] Protected skeleton content is preserved.
- [ ] Generated claims are JEA-authorized.
- [ ] Provenance, chronology, qualifications, and prohibited-claim boundaries are preserved.
- [ ] Material requirements receive appropriate visible emphasis.
- [ ] Distinctive authorized evidence is preserved when useful.
- [ ] Available page space is used effectively.
- [ ] Substantive roles have at least three strong results when evidence and space reasonably permit.
- [ ] No weak/repetitive content was added solely to fill space.
- [ ] WCM conforms to schema and matches the final resume.

## Output
Return the completed Targeted Resume and schema-conformant WCM.