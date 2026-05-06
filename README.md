# Snowglobe Skills for Claude Code

A Claude Code plugin that bundles five skills for working with [Snowglobe](https://guardrailsai.com/snowglobe), the simulation platform that stress-tests AI agents with synthetic users.

The skills auto-trigger by intent — you don't run them as slash commands. Just ask Claude what you want to do (e.g. "set up snowglobe for my project") and the right skill activates.

## What's inside

| Skill | What it does | Trigger phrases |
|---|---|---|
| `bootstrap-snowglobe-agent` | End-to-end onboarding: pip-installs `snowglobe`, runs `snowglobe-connect auth`, scans your code, drafts a chatbot description, scaffolds the wrapper file with `@snowglobe_tool` and `tool_defs()`, builds `.snowglobe/agents.json`, runs `snowglobe-connect test`, prompts you to `snowglobe-connect start`, and deep-links you to the dashboard | "bootstrap my snowglobe agent", "set up snowglobe for this project", "connect my chatbot to snowglobe" |
| `snowglobe-agent-description` | Writes an effective Snowglobe chatbot description from your code | "write a chatbot description for snowglobe", "describe my agent for simulation" |
| `app-description-writer` | Writes app descriptions that define application context, language, seed data, target users, workflows, and behavior logic for realistic simulations | "write an app description", "draft application context", "prepare seed data guidance" |
| `validate-snowglobe-agent` | Runs the validation suite against your `snowglobe_agent.py` and reports issues | "validate my snowglobe agent", "check my agent" |
| `analyze-fix-snowglobe-agent` | Runs validation + auto-fixes errors in place | "fix my snowglobe agent", "clean up my agent" |

## Install

In Claude Code:

```
/plugin marketplace add guardrails-ai/snowglobe-skills
/plugin install snowglobe-skills@snowglobe-skills
```

(Replace `guardrails-ai/snowglobe-skills` with your fork if you're using a fork.)

To update later:

```
/plugin marketplace update snowglobe-skills
```

## Usage

After install, just ask. Examples:

- *"Set up snowglobe for this project"* → `bootstrap-snowglobe-agent` runs the full bootstrap.
- *"Validate my snowglobe agent"* → `validate-snowglobe-agent` runs the validators.
- *"Fix the validation errors in my snowglobe agent"* → `analyze-fix-snowglobe-agent` repairs the file.
- *"Write a chatbot description for my agent"* → `snowglobe-agent-description` drafts it from your code.
- *"Write an app description for simulation"* → `app-description-writer` drafts structured application context.

Each skill is documented in its `SKILL.md` under [`plugins/snowglobe-skills/skills/`](plugins/snowglobe-skills/skills).

## Repository layout

```
snowglobe-skills/
├── .claude-plugin/
│   └── marketplace.json              ← marketplace catalog
├── plugins/
│   └── snowglobe-skills/
│       ├── .claude-plugin/
│       │   └── plugin.json           ← plugin manifest
│       └── skills/
│           ├── bootstrap-snowglobe-agent/
│           ├── snowglobe-agent-description/
│           ├── app-description-writer/
│           ├── validate-snowglobe-agent/
│           └── analyze-fix-snowglobe-agent/
└── README.md
```

## License

Apache-2.0 — see [LICENSE](LICENSE).
