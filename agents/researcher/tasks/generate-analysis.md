# Task: Generate Analysis

## Purpose
Analyze a target job against authoritative professional evidence and produce the strongest current JEA, including reconciliation of applicable factual uncertainties identified in supplied product feedback.

## Artifact Contract
Produce a Job Experience Analysis conforming to `/schemas/job-experience-analysis.yaml`.

Material Evidence Needs belong inside the JEA. This task does not produce formal Evidence Requests.

## Inputs
Required:
- Target Job Description.
- Current authoritative JERs.
- JEA schema.

Use current product feedback and other professional evidence when supplied and applicable.

## Method
### 1. Analyze the Target
Identify central mandate, material/knockout requirements, screening priorities, expected scope, and differentiators.

### 2. Reconcile Product Feedback
For each supplied factual/evidentiary uncertainty:
1. Check authoritative evidence.
2. If resolved, incorporate the applicable evidence.
3. If unresolved and materially investigable, create a Material Evidence Need.
4. If evidence establishes absence or mismatch, record the limitation.
5. If unsupported by authoritative state, do not adopt the feedback concern as fact.

### 3. Retrieve, Map, and Rank Evidence
Search broadly. Identify strongest and materially useful complementary evidence. Preserve qualifications, attribution, ownership, scope, limitations, and safe claim boundaries.

### 4. Identify Material Evidence Needs
Create one only when a factual dimension remains unresolved, materially affects analysis/claim safety, and human investigation could reasonably improve the state.

Do not create one for a conclusively absent capability or qualification.

### 5. Build Functional Role Architecture and Priority Evidence
Define concrete target-relevant professional functions and retain enough strongest/complementary evidence to make them credible.

### 6. Assess Fit
Evaluate overall fit, skill-area fit, differentiators, risks, genuine unsupported capabilities, and remaining Material Evidence Needs.

## Validation
- [ ] Output conforms to schema.
- [ ] Every material requirement is represented.
- [ ] Product-feedback uncertainties were independently checked.
- [ ] Resolved uncertainties use existing evidence.
- [ ] Investigable unresolved uncertainties become Material Evidence Needs when material.
- [ ] Known absent capabilities are limitations, not Evidence Needs.
- [ ] Evidence mappings are version-traceable.
- [ ] Complementary evidence is preserved when materially useful.
- [ ] Recommended Functional Roles have concrete support.
- [ ] No formal Evidence Request was generated.
- [ ] No unsupported facts were introduced.

## Output
Return the schema-conformant JEA.