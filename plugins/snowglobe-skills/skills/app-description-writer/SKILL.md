---
name: app-description-writer
description: >
  Writes or revises app descriptions for Snowglobe simulation fixtures across arbitrary
  applications. Trigger when the user asks to write an app description, draft application
  context, define target users and workflows, or prepare seed-data guidance for realistic
  persona and scenario generation.
---

# App Description Writer

Write app descriptions that give the simulator enough application, language, persona-seeding, and workflow context to generate realistic users and test target-agent behavior.

## Goal

An app description should answer:

- What application or assistant is being tested?
- What language should all customer-facing interaction use?
- What domain objects, policies, workflows, or user states exist?
- What minimal seed fields should personas include, based on the tool spec and workflow?
- Who are the target users?
- What user pains, motivations, and edge cases should drive conversations?
- What process should the user and assistant normally follow?
- What decisions, routing, actions, escalations, or constraints should be tested?

Prefer concrete application facts over marketing copy. The description is a simulation fixture, not a public app page.

## Required sections

Use these sections unless the app is genuinely too simple for one of them:

```markdown
# <App or Assistant Name>

## What it is

<One or two paragraphs explaining the assistant, channel, users, and core job.>

## Language

<Exact language requirement. Include locale when relevant, e.g. Brazilian Portuguese only.>

## Scope

<- In-scope features, workflows, entities, or support cases.
- Explicit out-of-scope items if they matter for testing.>

## Seed data and defaults

<Tables or bullets describing global defaults for seed data, access rules, limits, statuses, timestamps, feature flags, permissions, or policy constraints.>

Each persona needs to be seeded with at least:

- <required field derived from tool specs, target-agent instructions, or workflow state>
- <required field derived from tool specs, target-agent instructions, or workflow state>

Optionally:

- <optional field>
- <optional field with useful default>

## Target users

<Who should appear in generated personas. Include access conditions, geography, segment, exclusions, and scale if known.>

## Pain points

1. <A reason users contact or use the assistant.>
2. <A decision difficulty, uncertainty, operational blocker, or emotional concern.>

## User journey

1. <Entry point or opening situation.>
2. <Information the assistant should collect.>
3. <Checks, research, tools, or internal reasoning the assistant performs.>
4. <Options, answer, action, or next step presented to the user.>
5. <Follow-ups, preference changes, confirmations, or escalations.>

## Process

Step 1: <Operational step or decision point.>
Step 2: <Operational step or decision point.>
Step 3: <Expected outcome or fallback.>

## Behavior logic

<Rules, tables, priorities, routing choices, action requirements, escalation triggers, failure modes, or recommendation logic.>
```

## Section guidance

### What it is

Name the application or assistant, where it lives, and what concrete user problem it solves. Include whether it is conversational, transactional, advisory, support-oriented, creative, administrative, operational, or some combination.

Good:
- "A scheduling assistant for a clinic portal that helps patients find appointments, reschedule visits, and understand preparation instructions."
- "A support assistant inside an ecommerce app that helps customers track orders, request returns, and resolve delivery problems."

Avoid:
- Generic claims such as "a helpful assistant for users."

### Language

This section is mandatory. State the customer-facing language and locale directly.

Examples:
- "Portuguese only. All customer interactions are in Brazilian Portuguese."
- "Spanish only. All customer interactions are in Mexican Spanish."
- "English only. Use US English for all customer-facing messages."

If internal data uses another language, say whether the assistant should translate it for the customer.

### Scope

List every feature, workflow, support case, entity type, or user action the assistant can handle. Include short descriptions and constraints that materially affect conversation behavior.

Call out exclusions when they prevent bad test generation, such as unsupported workflows, unavailable account states, unavailable regions, non-MVP flows, human-only operations, or actions that require an external system.

### Seed data and defaults

Include stable defaults that persona generation and mock tools can rely on:

- Access, qualification, or enrollment states
- Required consent, permission, or authorization states
- Min and max values for important inputs
- Limits, quotas, thresholds, and validation rules
- Costs, deadlines, statuses, dates, durations, and expiration windows
- Allowed plan, booking, order, request, or configuration options
- Account, profile, order, ticket, device, booking, document, case, or shipment states
- Tool-visible identifiers the persona must know

Use a table when comparing similar entities, workflows, or states. Follow the table with explicit required and optional seed fields.

Required seed fields should be enough to run deterministic, varied simulations. Optional fields should include defaults when useful.

#### Choosing persona fields

Keep persona seed fields minimal. Start from the target-agent instructions and the tool definition/spec, then include only fields that are needed to make conversations and tool responses deterministic.

Before choosing fields, identify the relevant tool spec and whether there is a relevant PRD, product brief, or workflow document. If the tool spec location or source is unclear from the user's request, local files, or surrounding task context, ask the user where the tool spec lives before deciding required persona fields. Also ask whether there is a relevant PRD to consult when one is not already evident.

Review each tool in the spec:

- Identify required input parameters from JSON Schema `required` arrays, required function arguments, enum constraints, and parameter descriptions.
- Classify each required input as user-known, assistant-known, or system-known.
- Treat user-known required inputs as strong candidates for required persona fields, especially identifiers or facts the user would naturally provide.
- Treat system-known inputs as seed data or backend defaults, not necessarily as facts the simulated user should mention.
- Treat assistant-known or derived inputs as non-persona fields unless they affect user behavior or expected outcomes.

Use this rule of thumb: if removing a field would not change the user's goal, opening message, available actions, tool outputs, expected assistant behavior, or an important branch of the workflow, do not require it.

Required persona fields are appropriate when they:

- Supply a required tool input the user plausibly knows, such as an order ID, booking ID, account selector, item name, address, date, or requested value.
- Define the user's starting state in a way tools must reproduce, such as account status, active request, enrollment state, permission state, or case status.
- Determine the correct branch, such as whether an action is allowed, blocked, needs confirmation, or should escalate.
- Anchor a realistic opening or follow-up, such as the user's goal, preferred option, deadline, urgency, or target object.

Do not require persona fields when they:

- Are purely internal IDs that the assistant or backend can infer from session context.
- Are derivable from other seed fields.
- Only exist to satisfy mock implementation plumbing and are invisible to the user and behavior under test.
- Represent rare branch coverage knobs; make those optional with defaults or describe them as scenario variants.

When tool parameters are required but not user-known, document how they are supplied:

- session context
- seeded backend state
- default configuration
- prior tool output
- assistant selection from a list returned by a tool

### Target users

Define the persona population. Include:

- Geography or locale
- User or customer segment
- Access, qualification, or enrollment conditions
- Exclusions
- Typical starting situation
- Approximate population size, when known

### Pain points

Pain points should explain why conversations occur and what realistic users may worry about. Prefer behavioral or operational pain points over company goals.

Good pain-point categories:
- Awareness gaps
- Difficulty choosing between options
- Lack of confidence or domain knowledge
- Uncertainty during configuration, authorization, or submission
- Urgency, risk, or loss of access
- Friction from decentralized information, missing status, or unclear next steps

### User journey

Describe the normal end-to-end path from entry point to resolution. Include information collection, checks, tool-backed actions, user confirmations, and handoffs.

This section should make it clear how to test the assistant, not just what the assistant can say.

### Process

Use this section for repeatable backend or reasoning flow:

- Access, qualification, or permission checks
- Input validation and boundary checks
- Data lookup, research, comparison, or retrieval steps
- Status lookup or state transition order
- Consent, confirmation, or authorization sequence
- Restart conditions after user changes preferences
- Zero-result or blocked-flow fallback

### Behavior logic

State how the assistant should choose, rank, recommend, route, act, escalate, or refuse. Tables are useful when priority, access, state, or channel constraints change the correct answer.

Include fallback behavior for:

- No valid option, match, record, or path
- Missing consent, permission, or confirmation
- Out-of-range request
- Tool output conflicts
- User asks for unsupported action
- User changes the requested value, preference, workflow, or target object

## Quality checklist

Before finalizing, check that the app description:

- Has a mandatory `## Language` section with exact customer-facing locale.
- Says what the assistant is, where it lives, and what job it performs.
- Lists in-scope features, cases, workflows, entities, or actions with constraints.
- Defines required persona seed fields and useful optional fields.
- Provides default seed values for recurring application state, user state, and domain configuration.
- Defines target users and exclusions.
- Explains realistic user pain points.
- Describes the typical user journey and operational process.
- Captures behavior logic when more than one path can be correct.
- Avoids unsupported claims, hidden requirements, and vague domain language.
- Is specific enough that a tester can derive realistic success and failure conversations from it.

## Style

Use plain Markdown. Keep prose compact, but do not compress away app mechanics or testing-relevant constraints. Use bullets, numbered lists, and tables when they make behavior easier to compare.

Prefer terms that appear in application docs, tool schemas, seed schemas, or target-agent instructions. Do not invent capabilities that are not supported by the target agent or tools.
