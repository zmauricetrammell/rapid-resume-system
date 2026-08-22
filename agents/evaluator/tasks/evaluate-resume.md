# Task: Evaluate Resume

## Purpose
Evaluate whether the current Targeted Resume is the strongest truthful and effective product reasonably supported by the current state for the target job.

## Artifact Contract
This task produces a Resume Evaluation conforming to `/schemas/resume-evaluation.yaml`.

## Required Inputs
- Target Job Description.
- Current Targeted Resume.
- Corresponding WCM.
- Resume Evaluation schema.

Use supplied JEA, evidence, and product feedback when available and applicable.

## Method
### 1. Evaluate the Visible Product
Assess ATS, recruiter, and hiring-manager effectiveness: target identity, requirement visibility, specificity, credibility, differentiation, chronology, readability, and page utilization. Do not give external credit for internal-only information.

### 2. Verify Writer-Generated Content
Use WCM and supplied analytical state for generated/modified content. Do not require WCM entries for unchanged protected skeleton content.

### 3. Classify Every Material Finding
Use exactly one:
- **Product Defect:** current authorized state can materially improve the resume.
- **Evidence Uncertainty:** a material factual question remains unresolved and additional evidence could materially change the product.
- **Candidate Limitation:** authoritative state establishes a genuine mismatch with no unresolved factual question.

Do not convert a Candidate Limitation into a Product Defect merely because it creates screening risk.

### 4. Define Successful State
For Product Defects, define the successful visible product state.

For Evidence Uncertainties, define the factual condition that resolves the uncertainty, including supported and unsupported outcomes when useful. Do not prescribe who acts or how work is routed.

For Candidate Limitations, state the mismatch and likely external impact. Do not create remediation unless the resume misrepresents it.

### 5. Assess Submission Readiness
Mark not ready only when a material Product Defect remains or a material Evidence Uncertainty prevents confidence that this is the strongest truthful product reasonably available.

Do not block submission solely because the candidate does not meet a known requirement.

## Validation
- [ ] Output conforms to schema.
- [ ] External assessment uses visible resume content.
- [ ] Protected static content is not penalized for lacking WCM traceability.
- [ ] Every material finding uses the correct class.
- [ ] Known mismatches are not mislabeled as product defects.
- [ ] Evidence Uncertainties define factual resolution conditions without ownership/routing.
- [ ] Readiness reflects product quality rather than perfect candidate fit.

## Output
Return the schema-conformant Resume Evaluation.