---
name: bootstrap-snowglobe-agent
description: >
  End-to-end onboarding for a user who has never used Snowglobe before. Installs the `snowglobe`
  pip package, authenticates the CLI (skipping if already authed), registers the agent (POST to
  the Snowglobe API for new agents, or `snowglobe-connect init` to wire up existing ones), then
  creates the starter wrapper file via `init`. Scans the project to draft a chatbot
  description, augments the wrapper with `@snowglobe_tool` decorated functions, a `tool_defs()`
  function, `TOOLS_MAP`, and a tool-call loop in `completion()`, verifies with `snowglobe-connect
  test`, starts the wrapper with `snowglobe-connect start`, and hands the user a dashboard deep
  link.

  **Only trigger when the request explicitly mentions Snowglobe.** Ignore generic agent /
  chatbot / scaffolding phrasing that doesn't mention Snowglobe — other plugins may also handle
  agents and the user could mean one of those. Valid triggers: "set up snowglobe for my
  project", "bootstrap my snowglobe agent", "get started with snowglobe", "create a snowglobe
  agent", "connect my chatbot to snowglobe (for simulation/testing)", "scaffold my snowglobe
  agent", "add tools to my snowglobe agent". Do NOT trigger on bare "scaffold my agent",
  "set up my chatbot", "add tools to my agent", etc.
---

# Bootstrap Snowglobe Agent

Your job is to bootstrap a Snowglobe agent for the user end-to-end. By the end, the user has:

- The `snowglobe` Python package installed and the `snowglobe-connect` CLI on their PATH
- An authenticated session (`.snowglobe/config.rc`)
- A registered agent in the Snowglobe dashboard, with `.snowglobe/agents.json` mapping the
  wrapper file to its UUID — both produced by `snowglobe-connect init`
- A working Snowglobe agent file with tools wired up (`@snowglobe_tool`, `tool_defs()`,
  `TOOLS_MAP`, full `completion()` loop)
- A drafted chatbot description ready to paste into the dashboard
- A deep link to their agent in the Snowglobe UI: `https://guardrailsai.com/snowglobe/app/agents/<UUID>`

You may be operating in either of two modes:

- **From scratch:** no wrapper file exists yet. Step 3 handles agent registration (POST to the
  API for new agents, or matching an existing dashboard agent by name) and `init` creates the
  starter wrapper + writes `agents.json`. You then augment the wrapper with tools in Step 8.
- **Transforming existing:** there's already a wrapper file with an `agents.json` entry. Skip
  `init` (Step 3) and go straight to augmenting it.

Detect which mode you're in at the start of Step 3.

---

## Before you begin: tell the user the plan

The bootstrap touches the user's filesystem, their pip environment, their browser (for auth),
and their Snowglobe dashboard. Before running anything, print a short, numbered roadmap so the
user can see what's coming. This is for visibility, not approval — once you've printed the
plan, immediately start Step 1. Don't wait for the user to say "go" or "ok"; their invoking the
skill is the consent.

A good preamble for a from-scratch run looks like:

> Here's the plan:
> 0. **Pick the target agent** — if this repo has multiple agents, I'll ask which one (skipped if there's only one or you've already named a file)
> 1. **Install `snowglobe`** (pip) — needed for the CLI
> 2. **Authenticate** with `snowglobe-connect auth` — opens a browser briefly (skipping if you're already authed)
> 3. **Register the agent** — I'll ask whether you want a new agent (created via the Snowglobe API) or an existing one from your dashboard, then run `snowglobe-connect init` to wire it up locally
> 4. **Scan your project** to find existing tools, system prompts, and LLM client
> 5. **Draft a chatbot description** for your dashboard (I'll ask about gaps; feel free to skip). I'll PATCH it onto the agent record so it lands in your dashboard automatically — no copy-paste.
> 6. **Augment the wrapper file** with `@snowglobe_tool` decorators, `tool_defs()`, `TOOLS_MAP`, and a tool-call loop
> 7. **Verify** with `snowglobe-connect test`, then hand you the deep link to launch a simulation
>
> Starting now.

If you've already detected transforming-existing mode (existing wrapper file + matching
`agents.json` entry), trim the plan accordingly — drop Step 3 and frame Step 6 as "augmenting
your existing wrapper at `<path>`." If `snowglobe` is already installed and the user is already
authed, drop those too.

### Narrate each step as you go

Between steps, give a one-line update before running the command so the user knows where you
are in the plan. Examples:

- *"Step 1: installing the snowglobe package…"* → run pip install
- *"Already authed, skipping Step 2."* → continue
- *"Step 3: registering the agent. Are you creating a new agent or wiring up an existing one?"* → wait for answer, then drive `init`
- *"Scanning the project for tool functions…"* → read code
- *"Drafting a description from what I found. I'll ask about a couple of gaps."*
- *"Augmenting `snowglobe_agent.py` with `tool_defs`, `@snowglobe_tool`, `TOOLS_MAP`, and the tool-call loop in `completion()`."*

Brief is better than verbose — one line per step is plenty. The goal is that the user can
follow the bootstrap as it runs without having to inspect each tool call.

### When you ask the user a question, stop and wait

If a step requires a user answer (the new-vs-existing question in Step 3, the description
gap-fill in Step 6), **stop the turn after asking**. Don't run other tools, don't scan files,
don't try to "fill the wait" with parallel work. Send only the question and end the turn.

Concretely: never produce a message that contains both a question and a tool call (or an
announcement of one). Don't say *"While you answer, I'll scan the project for context"* — that
splits the user's attention and means you'll rework the scan if their answer changes anything.
The flow is strictly sequential: ask → user answers → resume with the next step.

This applies to every user-facing question in the skill. Single in-flight question per turn,
no side work.

---

## Step 0: Detect the target agent (especially in multi-agent repos)

Before installing or authenticating anything, figure out **which agent the user wants to wire
up**. Many real projects contain more than one agent definition (multi-agent systems, repos
with both prod and experimental agents, factories that generate multiple wrappers). Bootstrapping
the wrong one wastes the user's time and creates a confusing entry in the dashboard.

### a. Honor an explicit hint up front

If the user's invocation already names a file, YAML, or class — e.g. *"set up snowglobe for
`agents/credit_limit.yaml`"*, *"bootstrap snowglobe using `agent_factory.SnowglobeAgent`"* —
take that as the target and skip to Step 1. Don't second-guess by scanning.

### b. Otherwise scan for candidates

Run a light scan to see how many plausible agent definitions exist in the repo:

```bash
# YAML/JSON agent definitions
find . -type f \( -name "*.yaml" -o -name "*.yml" -o -name "*.json" \) \
  -not -path "*/node_modules/*" -not -path "*/.venv/*" -not -path "*/.git/*" \
  | xargs grep -l -i -E "agent|chatbot|assistant|prompt" 2>/dev/null | head -20

# Python files that look like agent definitions / factories / wrappers
find . -type f -name "*.py" \
  -not -path "*/node_modules/*" -not -path "*/.venv/*" -not -path "*/.git/*" \
  | xargs grep -l -E "def completion|class .*Agent|@snowglobe_tool|SnowglobeAgent|system_prompt" 2>/dev/null | head -20
```

Skim what comes back. A "candidate" is a file that clearly defines an agent's behavior — a
YAML spec, a class with a system prompt, a `completion()` function, a wrapper file already
referenced from `.snowglobe/agents.json`, etc. Build a short de-duplicated list.

### c. Decide whether to ask

- **Zero candidates**: proceed to Step 1 normally — there's nothing to disambiguate. You'll
  scaffold from scratch.
- **One candidate**: proceed to Step 1, but mention it in your preamble update ("targeting
  `<path>`") so the user can correct you before install runs.
- **Two or more candidates**: stop and ask the user before doing anything else. End the turn
  with only this question:

  > "This repo has multiple agent definitions. Which one should I wire up to Snowglobe?
  >
  > 1. `<path/to/agent_one.yaml>` — `<one-line summary lifted from the file>`
  > 2. `<path/to/agent_two.py>` — `<one-line summary>`
  > 3. `<path/to/agent_three>` — `<one-line summary>`
  >
  > (Reply with the number or the path. If multiple agents share scaffolding and you want
  > them all wired up, say so — I'll do them one at a time.)"

  After they answer, store the target path and proceed to Step 1. If they pick "all of them,"
  bootstrap the first one fully, then loop back to Step 3+ for each remaining one (skip the
  install/auth — those only run once).

### d. Detect project-managed scaffolding

While scanning, also look for project-level scaffolders that already produce Snowglobe
wrappers — e.g. `_generate_agents.py`, an `agent_factory.SnowglobeAgent`, a Makefile target,
or wrapper files that delegate to an internal service rather than calling an LLM SDK directly.
If you find one, that's a third bootstrap mode beyond from-scratch / transforming-existing:

- **Project-managed scaffolding mode**: follow the project's convention. Don't run
  `snowglobe-connect init` (it would produce a wrapper incompatible with the repo's pattern).
  Instead, use the existing factory/generator to produce the wrapper, then continue with
  Steps 4–9 to augment + verify + register.

Surface this to the user in your preamble:

> "I noticed this repo has its own Snowglobe scaffolding (`agent_factory.SnowglobeAgent` /
> `_generate_agents.py`). I'll follow that pattern instead of `snowglobe-connect init` — it
> would produce an incompatible standalone wrapper. Want me to proceed?"

If they confirm, set `MODE=project-managed` and skip the `init` substeps in Step 3 (the
agent still needs to be registered in the dashboard via API; just don't run `init`).

---

## Step 1: Install Snowglobe

Before anything else, make sure the `snowglobe` Python package is installed and the
`snowglobe-connect` CLI is available.

**Detect first:**

```bash
snowglobe-connect --help
```

If that succeeds, the CLI is installed — skip to Step 2.

**If not installed**, announce what you're doing in one short sentence ("Installing the
`snowglobe` package…") and run the install **without asking permission first**. The user
invoked this skill to set up Snowglobe; that is the consent.

```bash
pip install snowglobe
```

(If the project uses `uv`, `poetry`, or another tool, prefer that. E.g. `uv pip install snowglobe`,
`poetry add snowglobe`. Detect by checking for `pyproject.toml` + lockfile, or `uv.lock`.)

Verify the install by running `snowglobe-connect --help` again. If it still isn't on PATH after a
successful install, the user's shell may need to re-source — tell them to open a new terminal or
run `hash -r` (zsh/bash) and try again.

---

## Step 2: Authenticate (skip if already authed)

The user needs an authenticated Snowglobe CLI session before `init` can register an agent.

**Detect existing auth first.** Skip this step entirely if any of these is true:

- `.snowglobe/config.rc` exists and contains a non-empty `SNOWGLOBE_API_KEY=...` line
- The `SNOWGLOBE_API_KEY` environment variable is set in the user's shell

To check the file:

```bash
test -f .snowglobe/config.rc && grep -q '^SNOWGLOBE_API_KEY=..*' .snowglobe/config.rc && echo authed
```

To check the env var:

```bash
[ -n "$SNOWGLOBE_API_KEY" ] && echo authed
```

If either reports `authed`, mention "already authenticated, skipping auth" and continue to Step 3.

**If not authed**, announce what you're doing in one short sentence ("Running
`snowglobe-connect auth` — a browser will open for OAuth…") and run the command **without
asking permission first**. The user invoked this skill to set up Snowglobe; that is the consent.

```bash
snowglobe-connect auth
```

This creates `.snowglobe/config.rc` containing `SNOWGLOBE_API_KEY=...`.

If `auth` fails (e.g. headless environment, browser unavailable, callback timeout), *then* fall
back to telling the user to set the API-key env var manually:

```bash
export SNOWGLOBE_API_KEY=<key_from_dashboard>
```

…and re-run the skill. Don't preemptively offer the env-var path before attempting `auth`.

After auth, verify `.snowglobe/config.rc` exists (or the env var is set) before moving on.

---

## Step 3: Register the agent (API for new, `init` for existing)

The agent has to be registered in the Snowglobe dashboard before `init` can wire up the local
wrapper file. `snowglobe-connect init` only picks from existing dashboard agents — **it cannot
create a new one from the CLI.** So the flow forks:

- **New agent** → POST to the Snowglobe API to create it, then run `init` with the new name to
  wire it up locally.
- **Existing agent** → run `init` with the name piped to its stdin.

Both paths converge on `init` to produce the starter wrapper file (`snowglobe_agent.py`) and
the `.snowglobe/agents.json` entry.

**Detect skip condition first.** Skip this step entirely if a wrapper file already exists with
a matching `agents.json` entry — the user is in transforming-existing mode and just wants tools
added.

```bash
test -f .snowglobe/agents.json && \
  python -c "import json; d=json.load(open('.snowglobe/agents.json')); print(any((__import__('os').path.exists(k) for k in d)))"
```

If a wrapper + entry exist, set the target file path from the matching `agents.json` key and
proceed to Step 4. (If multiple wrappers are listed, ask the user which one to augment.)

**Otherwise, ask the scope question.** End the turn with only this question — no scanning,
drafting, or other tool calls until the user answers:

> "Are you creating a **new** Snowglobe agent for this project, or wiring up to an **existing**
> one in your dashboard?"

#### If the user said "new"

`init` can't create new apps, so create the agent via the public API first. Pick a sensible
default name from the project (the package's directory name in kebab-case — e.g.
`customer-support-agent`). Confirm with the user in one line *and end the turn*:

> "I'll create it as `customer-support-agent` and use 🤖 as the icon — sound good?"

After they confirm (or counter-suggest), do this **in two ordered steps** — the GET must come
before the POST. The agent-create endpoint requires `x-snowglobe-org-id` in addition to
`x-api-key`, and the org id isn't in `config.rc`.

**Step 3a — fetch the org id (must run before the POST):**

`GET /api/users/me` returns `{"id": "<user-id>", "organizations": [{"id": "<org-id>"}, ...]}`.
Take the first org's id:

```bash
KEY=${SNOWGLOBE_API_KEY:-$(grep -m1 '^SNOWGLOBE_API_KEY=' .snowglobe/config.rc | cut -d= -f2)}

ORG_ID=$(curl -sS https://api.snowglobe.guardrailsai.com/api/users/me \
  -H "x-api-key: $KEY" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print((d.get('organizations') or [{}])[0].get('id',''))")

# Validate before POSTing — if empty, the user has no org and the POST will fail anyway
if [ -z "$ORG_ID" ]; then
  echo "no organization on this account" >&2
  exit 1
fi
```

If `$ORG_ID` is empty, the user's account isn't in any organization. Stop and tell them:
*"Your account isn't in a Snowglobe organization yet. Add yourself to one in the dashboard at
https://guardrailsai.com/snowglobe/app, then re-run me."* Don't proceed to the POST and don't
guess an org id.

**Step 3b — only now POST the agent:**

```bash
curl -sS -X POST https://api.snowglobe.guardrailsai.com/api/agents \
  -H "x-api-key: $KEY" \
  -H "x-snowglobe-org-id: $ORG_ID" \
  -H "Content-Type: application/json" \
  -d '{"name": "customer-support-agent", "icon": "🤖"}'
```

The endpoint, schema, and auth headers are documented at
`/Users/zaydsimjee/workspace/threat-tester-demo/threat-tester-control-plane/src/sdk-spec.json`
under `AgentCreateSchema`. Required body fields are `name` (string) and `icon` (string — any
short emoji works). Description is optional.

The response is a JSON `Agent` object with an `id` field — that's the UUID. Capture it; you'll
also use the agent's name when running `init` next.

If the POST fails (4xx/5xx), surface the error to the user and stop. Common failures:

- `User must belong to an organization!` — you skipped Step 3a or the `x-snowglobe-org-id`
  header didn't get set. Re-run the GET and confirm `$ORG_ID` is non-empty before retrying.
- `422` — validation error (name conflict, missing icon). Show the error message verbatim.
- `401`/`403` — auth failed. Likely a stale `.snowglobe/config.rc`; ask the user to re-run
  `snowglobe-connect auth`.
- `499` — quota exceeded. The user has too many apps; they'll need to delete some.

After the POST succeeds, run `init` with the new agent's name piped to stdin so it picks the
just-created app from the (now-updated) dashboard list:

```bash
printf '%s\n' "customer-support-agent" | snowglobe-connect init
```

If `init` asks additional prompts (file path, etc.), extend the payload with `\n`-separated
answers. Empty lines accept defaults.

#### If the user said "existing"

Ask in one line and *end the turn*:

> "What's the agent called in your dashboard? A name or fragment is enough — I'll match it."

Once you have a name, run init with it piped:

```bash
printf '%s\n' "<name-or-fragment>" | snowglobe-connect init
```

If `init` errors with "no match" or "ambiguous," surface the error and ask them to
disambiguate. Don't fall back to "show me the list" — at 100+ apps that's useless.

#### After `init` completes

Read `.snowglobe/agents.json` to learn the wrapper file path it created (the most recent
entry) — that path is your target file for Step 8. Note the UUID too; you'll use it for the
deep link in Step 9.

If `init` fails for any reason, surface the error clearly and stop — don't try to substitute a
manual flow (asking the user for a UUID, hand-writing `agents.json`, scaffolding a wrapper
file from scratch). The whole point of using `init` is to avoid those substitutions.

---

## Step 4: Scan the project for grounding context

Scan the working directory for existing chat/agent application code. This grounds every later
step — domain vocabulary, tool implementations, system prompts, LLM client choice, model name,
and the description you draft for the dashboard.

Run something like:

```bash
find . -name "*.py" | head -40
```

Read any files that look like chat or agent apps. Cast a wide net — the project may use any
framework or LLM provider. Signals to look for:

**App / server patterns** (any of these count):
- Any web framework serving a chat or agent endpoint (`flask`, `fastapi`, `django`, `aiohttp`,
  `starlette`, `sanic`, plain `http.server`, etc.)
- A standalone script with a conversation loop or REPL
- A LangChain, LlamaIndex, AutoGen, CrewAI, or similar agent framework setup
- Any file that accepts a message list and returns a response

**Tool / function definitions** (any format counts):
- OpenAI-style `TOOLS` list (`"type": "function"` entries)
- LangChain `@tool` or `StructuredTool` definitions
- Anthropic tool dicts (`"name"`, `"input_schema"`)
- Plain Python functions that look like tool implementations (clear input/output, domain logic)
- Pydantic models or dataclasses describing tool inputs/outputs

**LLM client setup** (any provider counts):
- `openai`, `litellm`, `anthropic`, `cohere`, `mistral`, `groq`, `together`, `ollama`,
  `google.generativeai`, `boto3` (Bedrock), `azure`, `huggingface_hub`, etc.
- The model string being passed (e.g. `"gpt-4o-mini"`, `"claude-opus-4-7"`, `"mistral-large"`)

**Description signals:**
- System prompt strings — the agent's persona, tone, domain, and constraints
- Domain vocabulary — what the app is for (airline reservations, pizza ordering, HR helpdesk, etc.)
- README / docstrings / comments that describe who the bot is for and what it doesn't do

**Widget signals** (only relevant if the agent emits interactive UI elements
in its responses — buttons, dropdowns, multi-pick lists, free-text inputs):
- Code that returns or yields a `widgets` / `actions` / `quick_replies` list
  alongside the response text
- Frontend component names mentioned in the agent code: `Button`, `Select`,
  `Dropdown`, `MultiSelect`, `Checkbox`, `RadioGroup`, `Form`, `Input` etc.
- Branching logic on a "user clicked X" payload — schemas with `widget_id` /
  `action` / `option_id` shapes
- Server endpoints that handle callback payloads from interactive messages

If you find these, plan to wire widgets in Step 8 (see "Surfacing inline
widgets"). If not, skip the widget block — most agents are text-only.

Lift names, schemas, and implementations from the project rather than inventing placeholders.
If the project already has an LLM client/model the user is committed to, prefer it over the
default `init` template.

---

## Step 5: Decide which tools to scaffold

If the user named tools they want, use those. If the project has tool-like functions (per Step 4),
lift their names and signatures.

If **no tools are specified and none can be lifted**, scaffold with a single placeholder named
`example_tool`, clearly marked `# TODO`, so the user has a pattern to follow.

For each tool you'll scaffold, you need three things by Step 8:
- A spec entry in the `TOOLS` list (with `parameters`, `returns`, and `examples`)
- A `@snowglobe_tool` decorated implementation function
- An entry in `TOOLS_MAP`

---

## Step 6: Draft the chatbot description (and ask the user for gaps)

Snowglobe uses the chatbot description to generate realistic personas and scenarios for
simulation, so the description quality directly drives test quality. Per the
[Snowglobe description guide](https://guardrailsai.com/snowglobe/docs/guide/write-chatbot-description),
a good description naturally answers four questions:

1. **Functionality** — what does the chatbot do? (core value, primary purpose)
2. **Audience** — who uses it? (user types and their typical goals)
3. **Scope** — what can users ask? (kinds of questions, problems, tasks it handles)
4. **Boundaries** — what doesn't it do? (escalation triggers, refused topics)

**Style:** 2–3 sentences is enough to start. Specific but not exhaustive. User-value language,
not technical jargon. Don't include conversation examples — the dashboard has a separate slot
for historical data.

### Draft from code first

Use what you found in Step 4 to draft each of the four answers:

- **Functionality:** look at the system prompt, dominant tool names, and README.
- **Audience:** infer from domain vocabulary (e.g. "patients" vs "developers" vs "shoppers").
- **Scope:** look at what the tools actually do — they bound the supported tasks.
- **Boundaries:** look at refusal patterns in the system prompt or guardrails in the code.

### Then ask the user about gaps

For any of the four answers you can't confidently fill in from code, ask the user — but tell
them up front they can skip any question and you'll fall back to your inference. Frame it like:

> "I drafted a description from your code. I'm confident on functionality and scope, but
> wanted to check two things — feel free to skip either:
> 1. Audience: I assumed `<X>`. Anyone specific you have in mind?
> 2. Boundaries: anything the bot is not supposed to handle? (escalations, refused topics)"

Keep the final description to 2–6 sentences. Don't list every tool — describe capabilities at
the level of user value.

### Save the description to the agent record (don't make the user paste)

Once the description is finalized, **PATCH it onto the agent record** so it lands in the
dashboard automatically. The user should not have to copy-paste it from the terminal.

You'll need the agent's UUID. In from-scratch mode, you captured the `id` from the POST
response in Step 3b. In transforming-existing mode, read it from `.snowglobe/agents.json`:

```bash
AGENT_ID=$(python3 -c "import json; d=json.load(open('.snowglobe/agents.json')); print(next(iter(d.values()))['id'])")
```

(If `agents.json` lists multiple wrappers, pick the entry whose key matches the wrapper file
path you've been working with — not just the first entry.)

Then PATCH with the description. Same auth headers as Step 3b — note that in
transforming-existing mode you skipped Step 3, so `ORG_ID` may not be set yet. If it isn't,
fetch it the same way Step 3a does (`GET /api/users/me` → first org's id) before the PATCH.

```bash
KEY=${SNOWGLOBE_API_KEY:-$(grep -m1 '^SNOWGLOBE_API_KEY=' .snowglobe/config.rc | cut -d= -f2)}

if [ -z "$ORG_ID" ]; then
  ORG_ID=$(curl -sS https://api.snowglobe.guardrailsai.com/api/users/me \
    -H "x-api-key: $KEY" \
    | python3 -c "import json,sys; d=json.load(sys.stdin); print((d.get('organizations') or [{}])[0].get('id',''))")
fi

# Write the description to a temp file to avoid quoting hell with JSON-escaping
DESC_FILE=$(mktemp)
cat > "$DESC_FILE" <<'JSON'
{"description": "<the 2–6 sentence description you drafted, properly JSON-escaped>"}
JSON

curl -sS -X PATCH "https://api.snowglobe.guardrailsai.com/api/agents/$AGENT_ID" \
  -H "x-api-key: $KEY" \
  -H "x-snowglobe-org-id: $ORG_ID" \
  -H "Content-Type: application/json" \
  --data-binary @"$DESC_FILE"

rm "$DESC_FILE"
```

(In practice you'll build the JSON body in your tool call rather than running a heredoc —
the shape is `{"description": "..."}`.)

**Verify the response.** A successful PATCH returns the updated agent object. Confirm
`description` in the response matches what you sent. If the response has an empty/missing
`description` or a non-2xx status, surface the error to the user and fall back to the
manual paste flow (show the description, point them at the dashboard URL).

**Common failures:**
- `404` — wrong `AGENT_ID`. Re-read it from `agents.json` and retry.
- `401`/`403` — same auth issue as Step 3b. Re-run `snowglobe-connect auth`.
- `422` — description failed validation (too long, bad characters). Show the error and
  trim/sanitize the description before retrying.

After a successful PATCH, you can skip the "paste this into the dashboard" line in Step 9 —
just confirm to the user that the description was set, and still show it for their records.

---

## Step 7: Enrich tool descriptions from implementation

Before augmenting the wrapper file, read the actual implementation of each tool you identified
in Step 5. Snowglobe uses the `description`, `returns`, and `examples` fields to mock realistic
tool responses during simulation, so they need to encode behavior — not just interface shape.

For each tool:

1. **Read the full function body.** If the implementation lives in a separate file (e.g. `api.py`),
   read that file. Don't skim — look at every branch, every return, every data structure built.

2. **Extract:**
   - **Return shapes in practice** — exact field names, types, and value ranges (e.g. `status`
     is always `"confirmed"` / `"pending"` / `"cancelled"`)
   - **Realistic sample values** — concrete examples from the code (hardcoded values, enum
     strings, ID formats like `"FL-1234"`, price ranges)
   - **Branching behavior** — what conditions change the output? (e.g. "returns `{'error': ...}`
     when the flight number doesn't exist")
   - **Side effects / state assumptions** — does the tool mutate state, require a prior call,
     or depend on session data?

3. **Rewrite the `description` field** so a simulator reading only the description could
   produce plausible mocks. Plain prose, no JSON inside the string.

   Good:
   > "Look up a flight by flight number and return its current status and seat availability.
   > Returns a dict with keys: `flight_number` (string, e.g. 'FL-101'), `origin` (IATA code),
   > `destination` (IATA code), `departure_time` (ISO 8601), `status` (one of 'on_time',
   > 'delayed', 'cancelled'), `available_seats` (integer ≥ 0). If the flight number isn't
   > found, returns `{'error': 'Flight not found'}`. Seat counts typically range 0–30."

   Poor:
   > "Look up a flight."

4. **Update `examples`** to use values drawn from the implementation (hardcoded data, enum
   values, real ID formats).

5. **If no real implementation exists** (truly a stub), note in the description:
   *"Mock implementation — replace with real behavior before deploying."* Don't invent
   implementation details that aren't in the code.

---

## Step 8: Augment the wrapper file with tools

Open the wrapper file (created by `init` in Step 3, or pre-existing in transforming mode) and
add tools to it in place. Preserve everything `init` already put there: the imports, the LLM
client setup, and the existing `completion()` function.

What you're adding/modifying:

- **Imports**: add `from snowglobe.tools import snowglobe_tool` (and `import json` if missing)
- **`TOOLS` list**: full specs with `parameters`, `returns`, and `examples` (Step 7)
- **`tool_defs()` function**: returns `TOOLS`. The runner introspects it at startup. **Don't
  call `register_tools()` yourself** — the runner does that internally.
- **`@snowglobe_tool` decorated implementations**: one per tool, keyword-only args, dict return
- **`TOOLS_MAP`**: string name → function, for the dispatch loop
- **`completion()` body**: replace the basic LLM call with a tool-call loop that uses `TOOLS`
  in the request and dispatches via `TOOLS_MAP` when the model returns tool calls. Preserve
  the system prompt and LLM client/model that `init` (or the user) chose.

The structure should look like this:

```python
# Imports — preserve existing; add snowglobe.tools
from snowglobe.client import CompletionRequest, CompletionFunctionOutputs
from snowglobe.tools import snowglobe_tool
import json
# ... existing imports (openai, litellm, etc.) ...

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "<tool_name>",
            "description": "<enriched description from Step 7>",
            "parameters": {
                "type": "object",
                "description": "<overall description>",
                "properties": {
                    "<param>": {"type": "<json_type>", "description": "<...>"}
                },
                "required": ["<required_params>"]
            },
            "returns": {
                "type": "object",
                "description": "<return description>",
                "properties": { ... }
            },
            "examples": [{"input": { ... }, "output": { ... }}]
        }
    },
    # ... more tools ...
]

# tool_defs() — REQUIRED. Runner introspects this name at startup.
def tool_defs():
    return TOOLS

@snowglobe_tool
def <tool_name>(*, <param>: <type>, ...) -> dict:
    # TODO: replace with real implementation
    return { ... }  # mock response matching the "returns" schema

TOOLS_MAP = {
    "<tool_name>": <tool_function>,
}

def completion(request: CompletionRequest) -> CompletionFunctionOutputs:
    system_prompt = "..."  # preserve existing or add placeholder
    messages = request.to_openai_messages(system_prompt=system_prompt)

    while True:
        response = <client>.chat.completions.create(
            model="<model>",
            messages=messages,
            tools=TOOLS,
        )
        message = response.choices[0].message

        if not message.tool_calls:
            return CompletionFunctionOutputs(response=message.content)

        messages.append(message)
        for tool_call in message.tool_calls:
            if tool_call.function.name not in TOOLS_MAP:
                result = f"Error: Tool {tool_call.function.name} not found"
            else:
                result = TOOLS_MAP[tool_call.function.name](
                    **json.loads(tool_call.function.arguments)
                )
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })
```

### Canonical example (fully worked out)

```python
from snowglobe.client import CompletionRequest, CompletionFunctionOutputs
from snowglobe.tools import snowglobe_tool
from openai import OpenAI
import json
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_menu",
            "description": "Return the current pizza menu, optionally filtered by category. "
                           "Returns {'items': [{'name': str, 'price': float}, ...]}. Categories "
                           "are 'pizza', 'sides', 'drinks', or 'desserts'. If category is empty, "
                           "returns all items.",
            "parameters": {
                "type": "object",
                "description": "Parameters for fetching the menu",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Optional category filter: 'pizza', 'sides', 'drinks', or 'desserts'"
                    }
                },
                "required": []
            },
            "returns": {
                "type": "object",
                "description": "Menu items grouped by category",
                "properties": {
                    "items": {"type": "array", "description": "List of menu items"}
                }
            },
            "examples": [{
                "input": {"category": "pizza"},
                "output": {"items": [
                    {"name": "Margherita", "price": 12.99},
                    {"name": "Pepperoni", "price": 14.99}
                ]}
            }]
        }
    },
    {
        "type": "function",
        "function": {
            "name": "place_order",
            "description": "Place a pizza order and return a confirmation. Returns "
                           "{'order_id': str (e.g. 'ORD-001'), 'estimated_time': int (minutes), "
                           "'total': float}. Payment methods are 'card', 'cash', or 'online'.",
            "parameters": {
                "type": "object",
                "description": "Order details",
                "properties": {
                    "customer_name": {"type": "string", "description": "Full name of the customer"},
                    "items":         {"type": "array",  "description": "List of {name, quantity} dicts"},
                    "delivery_address": {"type": "string", "description": "Delivery address"},
                    "payment_method":   {"type": "string", "description": "'card', 'cash', or 'online'"}
                },
                "required": ["customer_name", "items", "delivery_address", "payment_method"]
            },
            "returns": {
                "type": "object",
                "description": "Order confirmation details",
                "properties": {
                    "order_id":       {"type": "string",  "description": "Unique order identifier"},
                    "estimated_time": {"type": "integer", "description": "Estimated delivery time in minutes"},
                    "total":          {"type": "number",  "description": "Total order cost"}
                }
            },
            "examples": [{
                "input": {
                    "customer_name": "Jane Smith",
                    "items": [{"name": "Pepperoni", "quantity": 1}],
                    "delivery_address": "123 Main St",
                    "payment_method": "card"
                },
                "output": {"order_id": "ORD-001", "estimated_time": 30, "total": 14.99}
            }]
        }
    }
]

def tool_defs():
    return TOOLS


@snowglobe_tool
def get_menu(*, category: str = "") -> dict:
    # TODO: replace with real implementation
    return {"items": [
        {"name": "Margherita", "price": 12.99},
        {"name": "Pepperoni", "price": 14.99},
    ]}

@snowglobe_tool
def place_order(*, customer_name: str, items: list, delivery_address: str, payment_method: str) -> dict:
    # TODO: replace with real implementation
    return {"order_id": "ORD-001", "estimated_time": 30, "total": 14.99}

TOOLS_MAP = {
    "get_menu": get_menu,
    "place_order": place_order,
}

SYSTEM_PROMPT = "You are a helpful pizza ordering assistant. Help customers browse the menu and place orders."

def completion(request: CompletionRequest) -> CompletionFunctionOutputs:
    messages = request.to_openai_messages(system_prompt=SYSTEM_PROMPT)

    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
        )
        message = response.choices[0].message

        if not message.tool_calls:
            return CompletionFunctionOutputs(response=message.content)

        messages.append(message)
        for tool_call in message.tool_calls:
            if tool_call.function.name not in TOOLS_MAP:
                result = f"Error: Tool {tool_call.function.name} not found"
            else:
                result = TOOLS_MAP[tool_call.function.name](
                    **json.loads(tool_call.function.arguments)
                )
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })
```

### Type annotation rules for `@snowglobe_tool` functions

- `"type": "string"` → `str`
- `"type": "integer"` → `int`
- `"type": "number"` → `float`
- `"type": "boolean"` → `bool`
- `"type": "array"` → `list` (or `list[dict]` if items are objects)
- `"type": "object"` → `dict`
- Optional params (not in `required`) → add ` = ""` or `= None` default

All parameters must be **keyword-only** (after `*`).

### `TOOLS` spec rules

Every entry must have:
- `"type": "function"` wrapper
- `"name"` and `"description"` inside `"function"`
- `"parameters"` with `"type": "object"`, `"properties"`, and `"required"` (empty list OK)
- `"returns"` block describing the return shape — Snowglobe uses this to generate mock outputs
- At least one `"examples"` entry with realistic `"input"` and `"output"`

### Surfacing inline widgets (only if the agent emits them)

**Skip this section unless Step 4 turned up widget signals.** Most agents
return plain text and don't need any of this.

If the agent renders interactive UI elements alongside its text response
(buttons, selects, multi-selects, free-text inputs), Snowglobe can simulate
real users clicking / picking / filling them. The contract:

- The customer's `completion()` may return `widgets=[Interaction(...)]` on
  `CompletionFunctionOutputs`. Snowglobe shows the persona those widgets,
  decides whether and how to interact based on each `description`, and
  sends the resulting `WidgetAction[]` back on the next turn.
- On that next turn, `completion()` receives those actions on
  `request.widget_actions` (typed list, may be empty).
- Optionally, when a widget click maps to a literal user phrase (e.g. an
  *Escalate to human* button really meaning the text `ESCALATE_TO_HUMAN`),
  set `CompletionFunctionOutputs.user_content` to rewrite the recorded
  user turn — downstream tools and reports see the canonical text.

**Imports** (add when widgets are involved):

```python
from snowglobe.client import (
    CompletionRequest, CompletionFunctionOutputs,
    Interaction, Button, Select, MultiSelect, Input, WidgetChoice,
)
```

**Four widget kinds in v1**, mapped to the action the persona produces:

| Widget        | Action emitted | Required field on `WidgetAction`         |
| ------------- | -------------- | ---------------------------------------- |
| `Button`      | `click`        | (none)                                   |
| `Select`      | `select_one`   | `option_id`                              |
| `MultiSelect` | `select_many`  | `option_ids` (`[]` clears)               |
| `Input`       | `set_text`     | `text_value` (`""` clears)               |

**Two key rules:**

1. **`description` drives the simulator.** Every `Interaction.description`,
   `widget.description`, and `WidgetChoice.description` is read by the
   persona generator. Write them like prompts to a real human — what the
   widget does, when to use it, how to interpret the choices. Vague
   descriptions = unrealistic widget interactions.
2. **Widget IDs come from production code.** Mirror the real `id` strings
   the customer's branching logic already keys off — don't invent new
   ones. If the user already calls a button `"talk_to_human"` in their
   app, use that exact id.

**Wrapper pattern.** Augment `completion()` to (a) handle inbound
`widget_actions`, (b) coerce the customer's emitted UI into `Interaction`
objects, (c) return them on the typed output:

```python
def completion(request: CompletionRequest) -> CompletionFunctionOutputs:
    # 1. React to any widget actions the persona took on the previous turn.
    inserted_user_content = None
    for action in request.widget_actions:
        if action.widget_id == "renew_card":
            # ... fire RENEW_CARD_TOOL or whatever the prod handler does
            ...
        elif action.widget_id == "escalate":
            inserted_user_content = "ESCALATE_TO_HUMAN"

    # 2. Run the existing completion pipeline (LLM call, tool loop, etc.)
    response = your_completion_cycle(request)

    # 3. Coerce any widgets the agent's UI layer emitted into Snowglobe types.
    interactions = [_to_snowglobe_interaction(g) for g in (response.widget_groups or [])]

    return CompletionFunctionOutputs(
        response=response.text,
        widgets=interactions or None,
        user_content=inserted_user_content,
    )


def _to_snowglobe_interaction(group):
    return Interaction(
        id=group.id,
        blocking=group.blocking,           # True for forms gated by Submit; False for one-off buttons
        title=group.title,
        description=group.description,
        widgets=[_to_snowglobe_widget(w) for w in group.widgets],
    )


def _to_snowglobe_widget(w):
    if w.kind == "button":
        return Button(id=w.id, label=w.label, description=w.description)
    if w.kind == "select":
        return Select(
            id=w.id, label=w.label, description=w.description,
            choices=[WidgetChoice(id=c.id, label=c.label) for c in w.choices],
        )
    if w.kind == "multiselect":
        return MultiSelect(
            id=w.id, label=w.label, description=w.description,
            choices=[WidgetChoice(id=c.id, label=c.label) for c in w.choices],
        )
    if w.kind == "input":
        return Input(id=w.id, label=w.label, description=w.description, placeholder=w.placeholder)
    raise ValueError(f"Unsupported widget kind: {w.kind}")
```

**`blocking` semantics:** set `blocking=True` for form-style interactions
where the customer's UI gates the next turn behind a submit click — the
persona stages select / input changes and only commits a turn when it
clicks a button. Set `blocking=False` for one-off buttons that don't
gate the next turn (the persona may act whenever the moment fits).

**Empty-prompt turns are legal.** A turn whose only "input" was a widget
click carries `request.messages[-1].content == ""` plus non-empty
`request.widget_actions`. Don't gate logic on `if request.messages[...].content`
alone — also check `request.widget_actions`.

**No widgets → no changes.** If `response.widget_groups` is empty, return
`widgets=None` and the wrapper PUT to control plane is byte-identical to
the pre-widgets behavior. Existing customers see no diff.

---

## Step 9: Verify, start the wrapper, and hand off

Tell the user the bootstrap is complete and walk them through verify → start → launch.

### a. Run the test

```bash
snowglobe-connect test <wrapper-file-path>
```

This sends a minimal request through `completion()` and checks the response shape. If it fails:
- "Tool X not found" → check `TOOLS_MAP` keys match the `name` fields in your `TOOLS` specs
- Missing `OPENAI_API_KEY` (or other provider key) → tell them to export it
- Import errors → confirm `snowglobe` is installed and the file imports run cleanly

### b. Start the wrapper

After test passes, the user runs `snowglobe-connect start` to bring the wrapper up. This is
what makes the agent reachable to the Snowglobe control plane during a simulation. It's a
long-running command — leave it running in a terminal.

```bash
snowglobe-connect start
```

Tell the user explicitly: **the simulation won't run unless this process is up.** They should
keep it running in one terminal while they launch a simulation from the dashboard.

### c. Final summary message

Tell the user:

1. **What was created/changed:**
   - `snowglobe` package installed (or already present)
   - `.snowglobe/config.rc` (from auth, or already present)
   - The wrapper file path (with `# TODO` markers flagged)
   - `.snowglobe/agents.json` entry (from `init`)

2. **The chatbot description** — the one you set on the agent via PATCH in Step 6. Show it
   as a quoted block so the user has it for their records and can tweak it if they want.
   Make clear that it's **already live in the dashboard** — no paste required. (If the PATCH
   failed in Step 6 and you fell back to the manual flow, instead tell them to paste it into
   the dashboard at the agent URL below.)

3. **Ask them to double-check the wrapper works** — particularly the tool implementations
   you stubbed. Recommend a quick smoke run if they have a real provider key.

4. **Remind them to start the wrapper** with `snowglobe-connect start` before launching a
   simulation, and to keep that terminal open.

5. **The deep link to launch a simulation:** read the UUID from `.snowglobe/agents.json` for
   the wrapper file you just augmented.

   > Once `snowglobe-connect start` is running, open your agent here to launch a simulation:
   > **https://guardrailsai.com/snowglobe/app/agents/\<UUID from agents.json\>**

6. **Assumptions you made** — preserved LLM client, model string, any inferred tool names/types
   — and invite corrections.

---

## What NOT to do

- Don't switch the LLM provider unless asked. `init` chose one; preserve it.
- Don't add tools the user didn't ask for (beyond one placeholder if none specified).
- Don't drop the existing system prompt if there is one — preserve and augment.
- Don't call `register_tools()` from the wrapper file. The runner does that internally; the
  user just defines `def tool_defs()` and the runner finds it by introspection.
- Don't hardcode the agent UUID into the wrapper file. The UUID lives in `.snowglobe/agents.json`,
  keyed by file path; the runner reads it from there.
- Don't return `CompletionFunctionOutputs(content=...)` — the field is named `response`.
- Don't ask the user to paste their agent UUID. Step 3 handles UUID acquisition automatically:
  for new agents via `POST /api/agents`, for existing via `init` matching by name.
- Don't ask the user to paste the chatbot description into the dashboard. Step 6 PATCHes it
  onto the agent record (`PATCH /api/agents/<id>` with `{"description": "..."}`) so it lands
  in the dashboard automatically. Manual paste is the fallback only if the PATCH genuinely
  fails (non-2xx) — and even then, surface the failure rather than silently degrading.
- Don't try to create a new agent via `snowglobe-connect init` — `init` only picks from
  existing dashboard agents. New agents must be created via `POST https://api.snowglobe.guardrailsai.com/api/agents`
  first (headers: `x-api-key: $SNOWGLOBE_API_KEY` **and** `x-snowglobe-org-id: <org-id>`,
  body `{"name": "...", "icon": "..."}`).
- Don't POST to `/api/agents` without the `x-snowglobe-org-id` header. The API rejects creates
  without it (*"User must belong to an organization!"*). Fetch the org id first via
  `GET /api/users/me` (returns `{"organizations": [{"id": "..."}]}`); take the first org's id.
  This GET must complete and return a non-empty org id BEFORE the POST runs — never POST first
  and try to "fix" by adding the header on retry.
- Don't ask the user which LLM provider/model to use. `init` writes a working default; if the
  project has its own LLM client (per Step 4), prefer that. Either way, you're not asking.
- Don't run `pip install snowglobe` without first checking whether it's already installed.
- Don't run `snowglobe-connect auth` without first checking whether the user is already authed.
- Don't ask permission before running `auth` or `pip install`. Announce what you're doing in
  one short sentence and run.
- Don't run `init` bare. Always pipe the agent name to its stdin
  (`printf '%s\n' "<name>" | snowglobe-connect init`). Reading and forwarding init's
  interactive prompts dumps the user's full app list back to them and stalls the flow.
- Don't queue other work into the same turn as a user-facing question. When you ask the user
  something (Step 3 new/existing, Step 6 description gaps), end the turn with just the
  question. No "while you answer, I'll do X" — wait, then continue.
- Don't substitute a manual flow if `init` fails (asking for UUID, hand-writing `agents.json`).
  Surface the `init` error and stop.
- Don't end the bootstrap without telling the user to run `snowglobe-connect start` and keep
  it running. Without that, simulations can't reach the wrapper.
- Don't add docstrings to every function — one-line comments only where genuinely useful.
- Don't add error handling beyond what's shown in the canonical pattern.
