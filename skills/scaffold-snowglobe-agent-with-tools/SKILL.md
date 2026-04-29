---
name: scaffold-snowglobe-agent-with-tools
description: >
  Transforms a basic Snowglobe agent (like new_agent.py) into a fully scaffolded agent
  with proper tool definitions, @snowglobe_tool decorated functions,
  tool_defs(), TOOLS_MAP, and a complete tool-call loop in completion(). Trigger when the
  user says "scaffold my agent", "add tools to my agent", "set up snowglobe tools", or
  similar requests to upgrade a bare-bones agent file for Snowglobe.
---

# Scaffold Snowglobe Agent

Your job is to transform a basic Snowglobe agent file into a fully scaffolded agent — with a
`TOOLS` list, `tool_defs()`, `@snowglobe_tool` decorated functions, `TOOLS_MAP`, and a complete
tool-call loop.

## Step 0: Explore the current directory for grounding context

Before doing anything else, scan the working directory for existing chat or agent application code.
This context tells you what domain the project is in, what tools already exist, and what patterns
to carry over into the Snowglobe scaffold.

Run the following (or equivalent) to discover relevant files:

```bash
find . -name "*.py" | head -40
```

Then read any files that look like chat or agent apps. Cast a wide net — the project may use any
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
- Pydantic models or dataclasses that describe tool inputs/outputs

**LLM client setup** (any provider counts):
- `openai`, `litellm`, `anthropic`, `cohere`, `mistral`, `groq`, `together`, `ollama`,
  `google.generativeai`, `boto3` (Bedrock), `azure`, `huggingface_hub`, or any other SDK
- The model string being passed (e.g. `"gpt-5.2"`, `"claude-opus-4-7"`, `"mistral-large"`)

**Other useful context:**
- System prompt strings — describing the agent's persona, domain, or constraints
- Domain vocabulary — what the app is for (e.g. airline reservations, pizza ordering, HR helpdesk)
- Mock / stub implementations of tool functions that can be carried over directly

Use what you find to inform every subsequent step:

- Lift tool names, schemas, and function implementations directly from the project rather than
  inventing placeholders.
- Reuse any existing system prompt.
- Keep the same LLM provider and model string already in use; only switch if the user asks.
- If no relevant files are found, note that and continue with the standard placeholder approach.

## Step 1: Identify the target file

Ask the user which file to scaffold if they haven't specified one. Look for files that import
`CompletionRequest`/`CompletionFunctionOutputs` from `snowglobe.client`. The canonical starting
point is a file like `new_agent.py` — minimal, with just a `completion()` function and no tools.

## Step 2: Read and analyse the agent file

Read the file. Determine:

1. **Does it already have tools?** Look for a `TOOLS` list, `tool_defs()`, or `@snowglobe_tool`
   decorators. If the file already has these, tell the user it looks already scaffolded and ask
   what they want to add or change.

2. **What LLM client does it use?** The file may use `openai`, `litellm`, `anthropic`, or another
   client. Preserve whatever client is already there. If it uses OpenAI directly, keep OpenAI. Only
   switch to litellm if the user asks.

3. **What model does it use?** Preserve the existing model string.

4. **Does the user want tools added, or just the scaffold structure?** If the user has mentioned
   specific tools they want (e.g., "I need a lookup_order tool"), collect those. Otherwise, add
   placeholder tools.

## Step 3: Determine tools to scaffold

If the user has provided tool definitions (JSON, a description, or existing function stubs), use
those as the basis for the tool specs and function signatures.

If **no tools are specified**, scaffold with **one placeholder tool** named `example_tool` so the
user has a clear pattern to follow. Make it clearly marked as a placeholder with a `# TODO` comment.

For each tool you scaffold, you need:
- The tool spec entry in `TOOLS` (with `parameters`, `returns`, and `examples`)
- A `@snowglobe_tool` decorated function with the correct kwargs and Python type annotations
- An entry in `TOOLS_MAP`

## Step 4: Enrich tool descriptions from implementation analysis

Before writing the output file, read the actual implementation of each tool you identified in
Step 3. The goal is to write `description` fields that give Snowglobe enough detail to generate
realistic mock responses — descriptions that encode the *behaviour* of the real implementation,
not just its interface.

For each tool function found in the project source:

1. **Read the full function body.** If the implementation lives in a separate file (e.g. `api.py`),
   read that file. Don't skim — look at every branch, every return statement, every data structure
   being constructed.

2. **Extract the following and note them down:**
   - **Return shapes in practice** — what field names, types, and value ranges does the real code
     produce? (e.g. `status` is always one of `"confirmed"`, `"pending"`, `"cancelled"`)
   - **Realistic sample values** — concrete examples drawn from the code (hardcoded values, enum
     strings, ID formats like `"FL-1234"`, price ranges, etc.)
   - **Branching behaviour** — what conditions change the output? (e.g. "returns an error dict when
     the flight number doesn't exist", "returns empty list when no seats available")
   - **Side effects or state assumptions** — does the tool mutate state, require a prior tool call,
     or depend on session data? Note these so Snowglobe can sequence interactions correctly.

3. **Rewrite the `description` field** for each tool in the TOOLS spec to include this information.
   The description should read as a concise but complete behavioural spec — enough that a simulator
   reading only the description could produce plausible mock outputs. Use plain prose; no JSON inside
   the description string.

   A good enriched description looks like:

   > "Look up a flight by flight number and return its current status and seat availability.
   > Returns a dict with keys: `flight_number` (string, e.g. 'FL-101'), `origin` (IATA code),
   > `destination` (IATA code), `departure_time` (ISO 8601 string), `status` (one of 'on_time',
   > 'delayed', 'cancelled'), `available_seats` (integer ≥ 0). If the flight number is not found,
   > returns `{'error': 'Flight not found'}`. Seat counts typically range from 0–30."

   A poor (pre-enrichment) description looks like:

   > "Look up a flight."

4. **Update the `"examples"` entries** as well — replace any placeholder examples with values drawn
   directly from the implementation (use the hardcoded data, enum values, and ID formats you found).

5. **If no real implementation exists** for a given tool (it's truly a stub or placeholder), note
   that in the description as: *"Mock implementation — replace with real behaviour before deploying."*
   Do not invent implementation details that aren't in the code.

After enriching all descriptions, proceed to write the file.

## Step 5: Write the scaffolded file

Produce a file that follows this exact structure:

```python
# 1. Imports — preserve existing ones, add snowglobe.tools import
from snowglobe.client import CompletionRequest, CompletionFunctionOutputs
from snowglobe.tools import snowglobe_tool
import json
# ... other existing imports ...

# 2. TOOLS list — full OpenAI-style tool specs with parameters, returns, examples
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "<tool_name>",
            "description": "<what it does>",
            "parameters": {
                "type": "object",
                "description": "<overall description>",
                "properties": {
                    "<param>": {
                        "type": "<json_type>",
                        "description": "<description>"
                    }
                },
                "required": ["<required_params>"]
            },
            "returns": {
                "type": "object",
                "description": "<return description>",
                "properties": { ... }
            },
            "examples": [{
                "input": { ... },
                "output": { ... }
            }]
        }
    },
    # ... more tools ...
]

# 3. tool_defs() — required by Snowglobe
def tool_defs():
    return TOOLS

# 4. @snowglobe_tool decorated functions — one per tool
# Each function:
#   - uses keyword-only args (*, kwarg: type)
#   - has valid Python type annotations matching the tool spec
#   - returns a dict (or appropriate type per spec)
#   - contains a stub/mock implementation
@snowglobe_tool
def <tool_name>(*, <param>: <type>, ...) -> dict:
    # TODO: replace with real implementation
    return { ... }  # mock response matching "returns" schema

# ... more tool functions ...

# 5. TOOLS_MAP — maps tool name strings to functions
TOOLS_MAP = {
    "<tool_name>": <tool_function>,
    # ...
}

# 6. completion() — full tool-call loop
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
                result = TOOLS_MAP[tool_call.function.name](**json.loads(tool_call.function.arguments))

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })
```

### Canonical example (fully worked out)

Use this as your reference for what a correctly scaffolded file looks like:

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
            "description": "Get the current menu for a pizza restaurant, optionally filtered by category",
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
                    "items": {
                        "type": "array",
                        "description": "List of menu items"
                    }
                }
            },
            "examples": [
                {
                    "input": {"category": "pizza"},
                    "output": {"items": [{"name": "Margherita", "price": 12.99}, {"name": "Pepperoni", "price": 14.99}]}
                }
            ]
        }
    },
    {
        "type": "function",
        "function": {
            "name": "place_order",
            "description": "Place a pizza order for a customer",
            "parameters": {
                "type": "object",
                "description": "Order details",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Full name of the customer"
                    },
                    "items": {
                        "type": "array",
                        "description": "List of items to order, each with name and quantity"
                    },
                    "delivery_address": {
                        "type": "string",
                        "description": "Delivery address for the order"
                    },
                    "payment_method": {
                        "type": "string",
                        "description": "Payment method: 'card', 'cash', or 'online'"
                    }
                },
                "required": ["customer_name", "items", "delivery_address", "payment_method"]
            },
            "returns": {
                "type": "object",
                "description": "Order confirmation details",
                "properties": {
                    "order_id": {"type": "string", "description": "Unique order identifier"},
                    "estimated_time": {"type": "integer", "description": "Estimated delivery time in minutes"},
                    "total": {"type": "number", "description": "Total order cost"}
                }
            },
            "examples": [
                {
                    "input": {
                        "customer_name": "Jane Smith",
                        "items": [{"name": "Pepperoni", "quantity": 1}],
                        "delivery_address": "123 Main St",
                        "payment_method": "card"
                    },
                    "output": {"order_id": "ORD-001", "estimated_time": 30, "total": 14.99}
                }
            ]
        }
    }
]


def tool_defs():
    return TOOLS


@snowglobe_tool
def get_menu(*, category: str = "") -> dict:
    # TODO: replace with real implementation
    return {"items": [{"name": "Margherita", "price": 12.99}, {"name": "Pepperoni", "price": 14.99}]}


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
            model="gpt-5.2",
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
                result = TOOLS_MAP[tool_call.function.name](**json.loads(tool_call.function.arguments))

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })
```

### Type annotation rules for @snowglobe_tool functions

Map JSON Schema types to Python types as follows:
- `"type": "string"` → `str`
- `"type": "integer"` → `int`
- `"type": "number"` → `float`
- `"type": "boolean"` → `bool`
- `"type": "array"` → `list` (or `list[dict]` if items are objects)
- `"type": "object"` → `dict`
- Optional parameters (not in `required`) → add ` = ""` or `= None` default
- For `list[dict[str, str|int]]` style when the items have mixed value types

All parameters must be **keyword-only** (after `*`).

### TOOLS list spec rules

Every tool entry in `TOOLS` must have:
- `"type": "function"` wrapper
- `"name"`, `"description"` inside `"function"`
- `"parameters"` with `"type": "object"`, `"properties"`, and `"required"` (even if empty list)
- `"returns"` block describing the return shape (Snowglobe uses this for simulation)
- At least one `"examples"` entry with a realistic `"input"` and `"output"`

## Step 6: Present the scaffolded file

Show the user the complete scaffolded file. Point out:
1. Each `# TODO` stub where they need to add real implementation
2. Any assumptions you made about tool names, types, or return shapes
3. Whether you preserved their existing LLM client and model

If the user gave you partial information (e.g., tool names but no parameters), note what you
inferred and invite them to correct it before implementing.

## What NOT to do

- Do not switch the LLM provider unless asked
- Do not add tools the user didn't ask for (beyond the minimum one placeholder if none specified)
- Do not remove the existing system prompt if there is one
- Do not add docstrings to every function — one-line comments only where needed
- Do not add error handling beyond what's shown in the canonical pattern above
