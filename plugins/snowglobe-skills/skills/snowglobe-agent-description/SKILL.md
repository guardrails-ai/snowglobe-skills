---
name: snowglobe-agent-description
description: >
  Writes effective agent descriptions for Snowglobe, the simulation platform that stress-tests AI agents
  by generating synthetic user interactions. Use this skill whenever the user wants to write, improve,
  or generate a **Snowglobe** chatbot description.

  **Only trigger when the request explicitly mentions Snowglobe (or simulation/testing of an
  agent in the Snowglobe sense).** Ignore generic "write a description for my agent" or "describe
  my chatbot" phrasing — those may belong to other plugins. Valid triggers: "write a description
  for Snowglobe", "write a snowglobe chatbot description", "describe my agent for snowglobe
  simulation", "I want to simulate [agent name] in Snowglobe". Also trigger when the user is
  configuring a snowglobe chatbot_wrapper.py or .snowglobe/agents.json and needs a description
  field.
---

# Snowglobe Agent Description Writer

Snowglobe simulates how real users will interact with an agent by generating diverse synthetic personas
and scenarios. The quality of these simulations depends meaningfully on the agent description —
it tells Snowglobe who the users are, what they want, and what the agent can do for them.

Your job is to read the relevant agent code and write a description that gives Snowglobe everything
it needs to generate realistic, useful simulations.

## Step 1: Identify which agent to describe

Before writing anything, you need to know the simulation target. **If the user hasn't explicitly
named an agent, always ask — even if you can make a reasonable guess.**

The reason asking matters: the description scope needs to match exactly what's being simulated.
Getting this wrong means Snowglobe generates the wrong kind of user personas and scenarios, which
defeats the purpose of running simulations. A quick clarifying question saves a lot of wasted output.

Scan the codebase briefly to understand the landscape, then ask. For example:

> "I can see this project has a triage/orchestrator entry point that routes
> to five specialist agents (flight info, booking, seats, FAQ, compensation). Which are you simulating?
> - The **full system** (users arrive with any travel request, routed to the right specialist)
> - A **specific subagent** — if so, which one?"

If the user has clearly named a specific agent (e.g., "write a description for the refunds agent"),
skip the question and proceed. But when the request is vague ("this project", "my agent", "the
chatbot"), ask before writing.

The description must be scoped to whatever is actually being simulated. A description for the
triage/orchestrator should reflect the breadth of topics users might raise. A description for a
specialist subagent should be narrower — focused on the kinds of users and tasks that agent handles.

## Step 2: Read the agent's definition

Read the agent's source code. Look for:
- **Instructions/system prompt** — what the agent is told to do, its persona, its workflow
- **Tools** — what actions it can take (these reveal functional scope)
- **Handoff description** — often a concise summary of the agent's role (great raw material)
- **Handoffs** — which other agents it routes to (tells you what it *doesn't* handle directly)
- **Input and output guardrails** — what topics and behaviors are out of scope

For a multi-agent system, also skim the orchestrator to understand how users enter the system
and how the target agent fits in.

## Step 3: Write the description

A Snowglobe agent description should be at least **2–4 sentences** that cover:

1. **What the agent does** and the value it provides to users (not how it's built)
2. **Who the users are** — their role, situation, and goals when they reach this agent
3. **What kinds of requests it handles** — be specific about task types, not just topics
4. **Where it draws the line** — what it escalates or can't help with (helps Snowglobe generate edge cases)

**If the agent renders interactive widgets** (buttons, selects, multi-selects,
inputs in the response — not background tools), mention them. Snowglobe can
simulate clicks, picks, multi-picks, and text-fills against widget interactions,
so naming them lets the persona generator exercise those branches. One sentence
is plenty:
> "The agent surfaces inline buttons for common next actions (e.g. *Renew card*,
> *Talk to a human*) and form widgets for structured updates."

### Calibrating scope to the simulation level

**Full system / orchestrator**: Describe the complete surface area. Users arrive with a wide range
of intents and the agent routes them. The description should reflect that breadth.

> "An airline customer service assistant that helps passengers manage their travel — including flight
> status, rebooking after delays, seat changes, baggage questions, and compensation for disruptions.
> Users are typically travelers mid-journey or planning upcoming trips who need quick, accurate help
> with their booking. The agent can look up flight details, make changes, and escalate to human agents
> for complex disputes."

**Specialist subagent**: Narrow the description to that agent's specific scope. Don't describe
the full system — describe only what a user interacting with *this* agent would experience.

> "A flight rebooking and cancellation agent for passengers whose travel plans have changed or been
> disrupted. Users arrive needing to cancel a booking, rebook onto a different flight, or find
> alternative options after a delay or cancellation. The agent can search for available flights,
> complete bookings, and hand off to the seat selection or compensation agent for follow-on needs."

### What to avoid

- **Technical implementation details**: no mention of LLMs, APIs, vector stores, model names
- **Vague generalities**: "helps users with their needs" — Snowglobe can't generate scenarios from this
- **Feature lists without context**: list what users *do*, not what the agent *has*
- **Conversation examples**: use Snowglobe's historical data upload for those instead
- **Overpromising scope**: if the agent only handles one domain, don't describe the whole system

## Step 4: Present and refine

Show the user the description and briefly explain the choices you made — especially around scope.
If you're uncertain about scope (e.g., the agent has broad handoffs but the user might only want
to test one branch), flag it and ask.

Offer a revised version if the user wants to adjust the scope, add constraints, or emphasize
certain user types or task categories.
