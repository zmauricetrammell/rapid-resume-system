# Task: Request Evidence

## Purpose

Transform one coherent unresolved factual issue into a focused Evidence Request suitable for human investigation.

## Artifact Contract

This task produces:

    Evidence Request

Authoritative schema:

    /schemas/evidence-request.yaml

Schema conformance is mandatory.

Do not substitute custom prose, an interview script, or an invented request format.

## Inputs

Required:

- A current factual issue within Researcher authority.
- Current authoritative professional evidence relevant to that issue.
- `/schemas/evidence-request.yaml`.

When the issue originates from a target-specific Material Evidence Need, use the current JEA and preserve its exact versioned context.

## Eligibility Check

Generate an Evidence Request only when all are true:

1. A material factual uncertainty exists.
2. Current authoritative evidence does not resolve it.
3. Human investigation could reasonably resolve or materially improve it.
4. The answer could materially affect professional evidence or target analysis.

Do not request evidence merely to improve wording, strengthen an already sufficient claim, or pursue a genuine unsupported capability.

## Method

### 1. Establish Current Evidence

Summarize what is already known.

Reference the exact JER versions and relevant evidence.

Do not ask the human to rediscover facts already established.

### 2. Define the Factual Issue

State:

- What remains unknown.
- Why it matters.
- Which factual dimensions are missing.
- What must not be assumed.

If target-specific, preserve:

- Target Job ID.
- JEA ID and version.
- Related requirement IDs.
- Originating Material Evidence Need ID when applicable.

If target-independent, leave target context null.

### 3. Identify Promising Professional Context

Reference professional episodes likely to help the human recall the answer.

Context should orient investigation, not pre-answer it.

### 4. Define Investigative Objectives

Objectives describe facts to establish, not exact interview questions.

Keep them narrow enough that the resulting Evidence Response can answer each objective directly.

### 5. Define Resolution Conditions

Specify:

- Full resolution.
- Partial resolution when meaningful.
- Related capability when relevant.
- Unsupported outcome.

Resolution conditions define factual states.

They do not classify eventual evidence strength, transferability, or job fit.

## Validation

Before completing:

- [ ] Output conforms to `/schemas/evidence-request.yaml`.
- [ ] The factual issue is material and investigable.
- [ ] Existing evidence is summarized so unnecessary rediscovery is avoided.
- [ ] Missing dimensions are explicit.
- [ ] Facts not to assume are explicit.
- [ ] Investigative objectives are factual and bounded.
- [ ] Full and unsupported resolution conditions are defined.
- [ ] Target context is present only when applicable.
- [ ] JEA-local identifiers are scoped to the exact JEA version.
- [ ] JER references include exact versions.
- [ ] The request does not prescribe evidence classification.
- [ ] The request does not contain workflow routing or corrective ownership.

## Output

Return the schema-conformant Evidence Request.

One Evidence Request should represent one coherent factual investigation. Split materially independent issues into separate requests.