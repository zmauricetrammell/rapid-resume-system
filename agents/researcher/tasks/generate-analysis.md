# Task: Generate Analysis

## Purpose

Analyze a target job against the authoritative professional evidence corpus and produce the strongest current Job Experience Analysis.

## Artifact Contract

This task produces:

    Job Experience Analysis

Authoritative schema:

    /schemas/job-experience-analysis.yaml

Schema conformance is mandatory.

Do not substitute custom Markdown, freeform prose, a legacy analysis format, or an invented structure.

Material Evidence Needs are recorded inside the JEA.

This task does not produce formal Evidence Requests.

## Inputs

Required:

- Target Job Description.
- Current authoritative Job Experience Records.
- `/schemas/job-experience-analysis.yaml`.

Use additional current professional evidence when available and within Researcher authority.

## Method

### 1. Analyze the Target Role

Identify:

- Central mandate.
- Material requirements.
- Knockout requirements.
- Screening priorities.
- Expected seniority and scope.
- Important differentiators.

Normalize requirements without weakening or expanding their meaning.

### 2. Retrieve Evidence Broadly

Search the full professional evidence corpus for each material requirement.

Do not stop after finding the first strong match.

Retrieve enough evidence to compare:

- Relevance.
- Ownership.
- Scope.
- Proficiency.
- Results.
- Specificity.
- Differentiation.

### 3. Map and Rank Evidence

For each requirement:

1. Identify the strongest evidence.
2. Classify its relationship and transferability.
3. Preserve qualifications and limitations.
4. Identify materially useful complementary evidence.

Distinguish:

    redundant evidence
    = substantially the same professional proof with less value

from:

    complementary evidence
    = adds a materially different professional dimension

Complementary dimensions may include:

- Different functional role.
- Different ownership.
- Different scale.
- Technical depth.
- Transformation leadership.
- Project or program delivery.
- Commercial context.
- Stakeholder leadership.
- Major quantified result.
- Recovery of a failed initiative.
- Professional progression.

Do not discard complementary evidence merely because another record already satisfies the requirement more strongly.

### 4. Determine Safe Claims

For each material requirement:

- Define the strongest supportable interpretation.
- Identify prohibited overstatements.
- Preserve attribution, scope, and ownership boundaries.
- Record evidence limitations.

Do not turn adjacent evidence into direct experience.

### 5. Identify Material Evidence Needs

Create a Material Evidence Need only when:

- A factual dimension remains unresolved.
- The unresolved fact materially affects analysis or claim safety.
- Human investigation could reasonably improve the evidence state.

Record:

- Current evidence.
- Missing dimension.
- Professional context.
- Facts not to assume.
- Materiality.
- Analytical impact.
- Current supported position.
- Claim constraints.

Do not create formal Evidence Requests in this task.

### 6. Build Functional Role Architecture

Use the selected evidence to define target-relevant professional functions.

For every proposed Functional Role, verify that selected evidence provides:

- Clear responsibility or ownership.
- Concrete work performed.
- Relevant scope.
- A meaningful result when available.
- Enough specificity to avoid generic presentation.

If a role is materially useful, retain enough complementary evidence to make it credible.

If there is not enough evidence to make the role concrete, do not recommend it.

### 7. Select Priority Evidence

Choose the smallest set that:

- Covers material requirements.
- Preserves the strongest evidence.
- Preserves complementary evidence that adds a distinct material dimension.
- Sustains the recommended Functional Role Architecture.
- Gives downstream presentation meaningful quantified or differentiated results.

Replace weaker evidence only when stronger evidence performs substantially the same analytical function.

Remove genuinely redundant or irrelevant evidence.

Do not over-prune relevant supporting evidence into generic role descriptions.

### 8. Assess Fit

Evaluate:

- Overall fit.
- Fit by material skill area.
- Differentiators.
- Material risks.
- Genuine unsupported capabilities.
- Remaining Material Evidence Needs.

A resume does not need a perfect match to be analytically valid.

## Validation

Before completing:

- [ ] Output conforms to `/schemas/job-experience-analysis.yaml`.
- [ ] Every material requirement is represented.
- [ ] Evidence mappings are traceable to exact JER versions.
- [ ] Every materially relevant JER was considered for unique analytical contribution.
- [ ] Major quantified or differentiated evidence was not omitted solely because another record satisfied the same requirement.
- [ ] Evidence removed as redundant was actually redundant rather than complementary.
- [ ] Ownership, scope, attribution, and results are accurately bounded.
- [ ] Every recommended Functional Role has concrete supporting evidence.
- [ ] Materially useful professional functions were not eliminated solely by requirement-level pruning.
- [ ] Material Evidence Needs meet the materiality and investigability standard.
- [ ] No formal Evidence Request was generated.
- [ ] No unsupported facts were introduced.

## Output

Return the schema-conformant Job Experience Analysis.

A short human-readable summary may accompany it, but the structured JEA is the authoritative output.