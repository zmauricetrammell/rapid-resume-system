# Task: Evaluate Resume

## Purpose
Evaluate whether the current Targeted Resume is the strongest truthful and effective product reasonably supported by the current state for the target job.

## Artifact Contract
This task produces:

    Resume Evaluation

Authoritative schema:

    /schemas/resume-evaluation.yaml

Schema conformance is mandatory.

A human-readable explanation may accompany the artifact, but it does not replace the schema-conformant Resume Evaluation.

## Required Inputs
- Target Job Description.
- Current Targeted Resume.
- Corresponding Writer Content Manifest.
- `/schemas/resume-evaluation.yaml`.

Use supplied JEA, professional evidence, prior evaluations, and other authoritative context when available and applicable.

## Method

### 1. Evaluate the Visible Product
Assess the resume as ATS, recruiter, and hiring-manager audiences would see it.

Evaluate:
- Target identity.
- Requirement visibility.
- Evidence specificity.
- Credibility.
- Differentiation.
- Chronology and clarity.
- Readability and page utilization.

Do not give external screening credit for information visible only in internal artifacts.

### 2. Verify Writer-Generated Content
Use the WCM and supplied analytical state to verify content generated or modified within Writer authority.

Do not require WCM traceability for unchanged protected Resume Skeleton content.

Protected static content may still be assessed for visible screening risk or for a factual conflict explicitly established by authoritative state.

### 3. Classify Every Material Finding
Every material finding must use exactly one `finding_class` defined by the schema:

**Product Defect**
- The resume can be materially improved using current authorized state.
- Examples: authorized evidence omitted, unsupported wording, avoidable ambiguity, weak page utilization when additional authorized evidence exists, or Resume/WCM mismatch.

**Evidence Uncertainty**
- A material target-relevant factual question remains unresolved.
- Current state does not conclusively establish support or absence.
- Additional factual evidence could materially change the strongest truthful product.
- Define both supported and unsupported factual outcomes.

**Candidate Limitation**
- Authoritative state establishes that the candidate does not possess a requested qualification, capability, experience, or scope.
- No material factual uncertainty remains.
- Report the fit/screening risk without treating it as a resume defect.

Do not classify a truthful irreducible mismatch as a Product Defect.

### 4. Determine Blocking Status
`blocks_submission` may be true only for a material Product Defect or Evidence Uncertainty.

A Candidate Limitation must never block submission.

A nonblocking Product Defect or Evidence Uncertainty may remain when the resume is still the strongest truthful product reasonably available and the issue does not create substantial avoidable screening risk.

### 5. Define Successful State
For a Product Defect:
- Define the successful visible product state.

For an Evidence Uncertainty:
- Define the factual state needed to resolve the uncertainty.
- Record supported and unsupported outcomes.
- Do not prescribe who investigates, who rewrites, where work is routed, or what workflow step occurs.

For a Candidate Limitation:
- State the settled truthful condition and likely screening impact.
- Do not invent remediation for an irreducible limitation.

### 6. Assess Submission Readiness
A resume is `ready_to_submit` when it is the strongest truthful presentation reasonably supported by current professional and analytical state and no blocking finding remains.

A resume is `not_ready_to_submit` only when one or more material Product Defects or Evidence Uncertainties block readiness.

`weak_fit_reconsider_application` may be used when candidate limitations or overall fit make the application strategically weak, but this is a fit judgment rather than a product-remediation state.

Do not block submission solely because the candidate does not meet a known requirement.

## Validation
Before completing:

- [ ] Output conforms to `/schemas/resume-evaluation.yaml`.
- [ ] All required schema fields are present.
- [ ] External assessment uses only visible resume content.
- [ ] WCM verification is limited to Writer-generated or modified content.
- [ ] Every material finding is classified as `product_defect`, `evidence_uncertainty`, or `candidate_limitation`.
- [ ] Every Evidence Uncertainty defines supported and unsupported outcomes.
- [ ] Every Candidate Limitation has `blocks_submission: false`.
- [ ] `blocking_finding_ids` contains only blocking Product Defects or Evidence Uncertainties.
- [ ] Submission readiness reflects product readiness rather than perfect candidate fit.
- [ ] No finding assigns corrective ownership, routing, or a downstream agent.
- [ ] Human-readable prose does not replace the schema-conformant artifact.

## Output
Return the schema-conformant Resume Evaluation.

A concise human-readable summary may accompany it.