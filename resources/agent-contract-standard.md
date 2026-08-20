# Rapid Resume System — Agent Contract Standard V2.0

**Template Version:** 2.0
**Applies To:** All Rapid Resume System agents
**Maintained By:** Agent Architect
**Purpose:** Standardize the structure, authority, boundaries, validation rules, and handoff behavior of all agent contracts.

---

# 1. ROLE

Define who the agent is within the Rapid Resume System.

State:

* The agent's professional function.
* Its fundamental responsibility.
* The primary question it exists to answer.
* What distinguishes this agent from the other agents.
* What the agent is explicitly not responsible for.

Keep this section concise. It establishes identity, not procedure.

---

# 2. MISSION

Define the outcome the agent is responsible for achieving.

The Mission should describe the desired end state of the agent's work rather than the steps it performs.

A strong Mission statement should answer:

> What must be true when this agent has successfully completed its role?

The Mission should remain stable across different task types.

---

# 3. RESPONSIBILITIES

Define the persistent functions owned by this agent.

Responsibilities describe what the agent is expected to perform regardless of the specific task being executed.

1. [Responsibility]
2. [Responsibility]
3. [Responsibility]

Responsibilities should:

* Describe durable role ownership.
* Avoid task-specific procedures.
* Avoid duplicating another agent's responsibilities.
* Be specific enough to establish accountability.

---

# 4. AUTHORITY

Define the decisions and actions this agent is authorized to perform independently.

Authority establishes the decentralized decision rights of the agent.

## The Agent May

* [Authorized decision or action]
* [Authorized decision or action]

## The Agent Must

* [Mandatory behavior]
* [Mandatory behavior]

## The Agent Must Not

* [Unauthorized action]
* [Unauthorized decision]

Authority should answer:

> What decisions may this agent make without approval from another agent or human?

The contract should grant enough authority for the agent to complete its assigned work and hand it off independently.

---

# 5. INPUTS

Define the information and artifacts the agent may consume.

## Required Inputs

* [Input]
* [Input]

The task cannot normally be completed without these inputs.

## Optional Inputs

* [Input]
* [Input]

Optional inputs may improve quality, provide historical context, or support verification but are not always required.

For structured inputs, reference the authoritative schema rather than reproducing the schema inside the contract.

Example:

```text
Job Experience Analysis
Schema: /schemas/job-experience-analysis.yaml
```

Contracts should not contain duplicate copies of shared schemas.

---

# 6. INPUT AUTHORITY AND PRECEDENCE

Define how the agent interprets competing or conflicting inputs.

List authoritative sources in descending order of precedence where appropriate.

Example:

1. Confirmed factual source records.
2. Current target-job materials.
3. Structured analysis artifacts.
4. Previous outputs or revision records.
5. Supplemental contextual material.

For each important input type, establish whether it:

* Establishes factual truth.
* Establishes target requirements.
* Authorizes a claim.
* Provides guidance only.
* May be challenged or re-evaluated.
* Must not be silently overridden.

When sources conflict, the agent must follow this precedence rather than resolving contradictions through assumption.

---

# 7. OUTPUTS

Define the artifacts and decisions this agent is authorized to produce.

## Primary Outputs

* [Output]
* [Output]

## Conditional Outputs

Outputs produced only under defined circumstances:

* [Gap request]
* [Revision request]
* [Human-input request]
* [Failure or blocker]
* [Other conditional artifact]

For structured outputs, reference the authoritative schema rather than embedding it.

Example:

```text
Experience Gap Request
Schema: /schemas/experience-gap-request.yaml
```

## Handoff Destinations

Define the normal recipient for each output.

```text
[Output A] → [Agent]
[Output B] → [Agent]
[Output C] → [Human]
```

The agent should route work according to the contract without requiring centralized orchestration.

---

# 8. OPERATING PRINCIPLES

Define the permanent reasoning principles that govern the agent across all tasks.

These are role-specific doctrines rather than procedures.

Examples may include:

* Capability over billet.
* Evidence over inference.
* Professional translation rather than organizational reproduction.
* Visible resume evidence over hidden supporting evidence.
* Collaborative evidence discovery.
* Preserve provenance.
* Deterministic structure compliance.
* Requirement relevance over general career impressiveness.

Operating Principles should explain **how the agent should think**, not provide step-by-step task instructions.

---

# 9. ROLE BOUNDARIES

Define the division of responsibility between agents.

## This Agent Owns

* [Function]
* [Function]

## Researcher Owns

* [Function]

## Writer Owns

* [Function]

## Evaluator Owns

* [Function]

## Interviewer Owns

* [Function]

Include only roles relevant to the boundary being established.

The contract must explicitly identify when the agent must hand work to another role instead of performing that role itself.

The agent must not silently expand its own authority because another agent has not yet completed its work.

---

# 10. DECISION RULES

Define the rules the agent uses to make recurring judgments.

Examples include:

* How evidence is ranked.
* How requirements are prioritized.
* When evidence is direct versus transferable.
* When a gap exists.
* When a claim is sufficiently supported.
* When new factual evidence is required.
* When a revision is sufficient.
* When work is ready for handoff.
* When the candidate or human operator must be consulted.

Decision rules should be deterministic wherever practical.

When judgment remains subjective, define:

* Relevant criteria.
* Required evidence.
* Confidence expectations.
* How uncertainty should be represented.

---

# 11. QUALITY AND VALIDATION REQUIREMENTS

Before handing off completed work, the agent must validate its output.

## Common Validation Requirements

* [ ] Required inputs were available or missing inputs were explicitly identified.
* [ ] Required outputs were produced.
* [ ] Structured outputs conform to the authoritative schema.
* [ ] The agent remained within its role authority.
* [ ] Factual claims remain supported.
* [ ] Provenance was preserved.
* [ ] Attribution and ownership were preserved.
* [ ] Known uncertainty was disclosed.
* [ ] Unsupported assumptions were not introduced.
* [ ] Required handoff conditions were satisfied.

## Agent-Specific Validation Requirements

* [ ] [Validation]
* [ ] [Validation]
* [ ] [Validation]

Validation should occur before the work item leaves the agent's Kanban stage.

---

# 12. FAILURE, BLOCKING, AND ESCALATION CONDITIONS

Define conditions under which the agent cannot safely or correctly complete its work.

Examples:

* Required input is absent.
* Required input does not conform to schema.
* Evidence conflicts.
* Evidence cannot support a requested claim.
* A factual question cannot be resolved without human input.
* Another agent must perform additional work.
* Required source material is inaccessible.
* Confidence is insufficient for a material decision.

For each condition, define the appropriate response.

Example:

```text
Condition:
Required professional evidence may exist but cannot be located.

Action:
Generate Researcher recheck request.

Destination:
Researcher.
```

The agent must not compensate for missing information by inventing facts, silently broadening claims, or assuming another agent's authority.

---

# 13. COMPLETION CONDITIONS

Define the agent's **Definition of Done**.

These conditions determine when the work item may leave the agent's ownership and move to the next Kanban stage.

The agent's work is complete only when:

* [Completion condition]
* [Completion condition]
* [Completion condition]

Completion conditions should be observable and testable wherever practical.

If the conditions are not satisfied, the agent should either:

* Continue working;
* Generate the appropriate request;
* Route the work backward or sideways to the appropriate owner;
* Request human input;
* Mark the work as blocked.

The agent must not declare completion solely because it has produced an output.

---

# 14. PROHIBITED BEHAVIORS

Define hard constraints that apply regardless of task.

Use this section only for behaviors that are always prohibited.

Examples:

* Never fabricate professional experience.
* Never manufacture metrics.
* Never change factual provenance to improve job fit.
* Never represent transferable experience as direct experience without support.
* Never perform another agent's role merely to avoid a handoff.
* Never silently resolve contradictory evidence.
* Never treat classification metadata as independent factual evidence.

Do not use this section for preferences or ordinary quality guidance.

---

# 15. ROLE-SPECIFIC DOCTRINE

Use this section only when an agent requires substantial conceptual guidance unique to its function.

The section may contain multiple subsections.

Examples:

## Researcher

* Capability Over Billet
* Career-Wide Evidence Retrieval
* Direct vs. Transferable Evidence
* Functional Role Classification

## Interviewer

* Collaborative Interview Posture
* Memory Development
* Positive Narrative Development
* Evidence Confirmation

## Writer

* Professional Translation
* Functional Role Presentation
* Content Authorization
* Deterministic Skeleton Compliance

## Evaluator

* Recruiter Simulation
* Three Screening Perspectives
* Evidence vs. Mention
* Corrective-Action Classification

Role-Specific Doctrine may be detailed, but it must remain permanent role behavior rather than task procedure.

---

# 16. CONTRACT INTERFACE

Provide a concise summary of the agent's place in the decentralized workflow.

## Accepts

```text
[Artifact / Message] ← [Source Agent or Human]
[Artifact / Message] ← [Source Agent or Human]
```

## Produces

```text
[Artifact / Message] → [Destination Agent or Human]
[Artifact / Message] → [Destination Agent or Human]
```

## May Return

```text
[Clarification / Rework Request] → [Agent]
[Evidence Request] → [Agent]
```

## Human Interaction

Specify one:

```text
None
```

or:

```text
Permitted under defined conditions
```

or:

```text
Required for specific tasks
```

Then define those conditions.

## Normal Kanban Transition

```text
[Previous Owner] → [This Agent] → [Next Owner]
```

## Exception Transitions

```text
[This Agent] → [Agent] when [condition]
[This Agent] → Human Input when [condition]
```

This section serves as the concise workflow-facing interface for implementation.

---

# CONTRACT / TASK / SCHEMA SEPARATION

All Rapid Resume System artifacts must preserve the following separation.

## Contract

Answers:

* Who is this agent?
* What is its mission?
* What responsibilities does it own?
* What decisions may it make?
* What information may it trust?
* What must it never do?
* When is its work complete?
* When must it hand work elsewhere?

Location:

```text
/agents/[agent]/contract.md
```

## Task Instruction

Answers:

* What task is the agent performing now?
* What task-specific inputs apply?
* What procedure should it execute?
* What output is required for this invocation?

Location:

```text
/agents/[agent]/tasks/[task-name].md
```

Task instructions may specialize a contract but must not contradict or redefine it.

## Schema

Answers:

* What structure must a shared artifact use?
* Which fields are required?
* What values and relationships are permitted?

Location:

```text
/schemas/[schema-name].yaml
```

Schemas define communication interfaces between agents and must not be duplicated inside contracts or task instructions.

## Resource

Answers:

* What external or shared material does the agent operate on?

Examples:

* Resume skeleton.
* Prompt bank.
* Job description.
* Supporting documents.
* Formatting resources.

Resources should remain separate from agent behavior definitions.

---

# CONTRACT AUTHORING RULES

When creating or revising an agent contract:

1. Use this section order consistently.
2. Keep role identity separate from task procedure.
3. Define explicit decision authority.
4. Define explicit ownership boundaries.
5. Reference shared schemas rather than reproducing them.
6. Give the agent enough authority to operate independently within its Kanban stage.
7. Define clear completion criteria before permitting handoff.
8. Define failure and exception routing rather than relying on a central orchestrator.
9. Preserve factual integrity and provenance across all agent interactions.
10. Avoid duplicate rules when a single higher-level rule is sufficient.
11. Put permanent reasoning doctrine in the contract.
12. Put invocation-specific procedures in task instructions.
13. Put structured data definitions in schemas.
14. Prefer observable, testable rules over vague quality language.
15. Preserve role specialization; an agent should hand off work rather than absorb another role's responsibilities.
16. Ensure every contract can be understood independently without requiring hidden conversational context.

---

# ARCHITECT REVIEW CHECKLIST

Before approving a new or revised contract, the Agent Architect should verify:

* [ ] The Role clearly identifies the agent.
* [ ] The Mission defines an observable end state.
* [ ] Responsibilities are persistent rather than task-specific.
* [ ] Authority clearly states what the agent may and may not decide.
* [ ] Required and optional inputs are identified.
* [ ] Input precedence is defined where conflicts are possible.
* [ ] Outputs and destinations are explicit.
* [ ] Operating Principles describe durable reasoning doctrine.
* [ ] Boundaries clearly separate this agent from other roles.
* [ ] Decision Rules cover recurring material judgments.
* [ ] Validation requirements can detect incomplete or unsafe work.
* [ ] Failure and blocking conditions have defined destinations.
* [ ] Completion Conditions create a clear Definition of Done.
* [ ] Prohibited Behaviors contain only hard constraints.
* [ ] Role-Specific Doctrine contains no task-specific procedure.
* [ ] Contract Interface accurately reflects Kanban handoffs.
* [ ] Shared schemas are referenced rather than duplicated.
* [ ] Task instructions have not leaked into the contract.
* [ ] The contract does not depend on a central orchestrator.
* [ ] The agent can independently accept, process, validate, and hand off a work item within its authority.
