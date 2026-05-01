---
name: validate-snowglobe-agent
description: >
  Validates a target snowglobe_agent.py by running a suite of code-based validation scripts.
  Trigger when the user says "validate my agent", "run validation on my agent", "check my
  snowglobe agent", or similar requests to verify a Snowglobe agent file is correct.
---

# Validate Snowglobe Agent

Your job is to run the validation suite against a target `snowglobe_agent.py` and report the
results clearly.

## Step 1: Identify the target file

If the user has not specified a file, look for a `snowglobe_agent.py` in the current working
directory or its immediate subdirectories. If you find exactly one, use it. If you find multiple
or none, ask the user which file to validate.

## Step 2: Locate the skill directory

The validators live alongside this skill file. Find the skill directory by running:

```bash
find . -path "*/validate-snowglobe-agent/run_validators.py" | head -1
```

Strip the filename — that directory is `<skill_dir>`. Everything below runs relative to it.

## Step 3: Ensure the venv exists

Check whether `<skill_dir>/.venv` exists. If not, create it:

```bash
python3 -m venv <skill_dir>/.venv
```

The venv python is at `<skill_dir>/.venv/bin/python`. Use this python for all subsequent
commands — never the system python.

If any validators declare dependencies in a `requirements.txt` alongside this SKILL.md, install
them now:

```bash
<skill_dir>/.venv/bin/pip install -q -r <skill_dir>/requirements.txt
```

Skip the pip step if no `requirements.txt` exists.

## Step 4: Extract tool definitions

Read the target file and extract the tool definitions yourself. Look for:
1. A `tool_defs()` function body that returns a list of dicts
2. `@snowglobe_tool` decorated function definitions
3. A `TOOLS_MAP` dict whose values are tool spec dicts

Write the extracted definitions as a JSON array to `tool_defs.json` in the **same directory as
the target file**. The array should contain OpenAI-style tool spec dicts exactly as they would
be returned by `tool_defs()`. If no tool definitions exist, write `[]`.

Example:
```bash
# You write this file before running the validators
<path/to/tool_defs.json>
```

## Step 5: Run the validation suite

Run the validator runner through the venv python:

```bash
<skill_dir>/.venv/bin/python <skill_dir>/run_validators.py <path/to/snowglobe_agent.py>
```

The runner will:
1. Read `tool_defs.json` from the same directory as the target file.
2. Pass the file path as `sys.argv[1]` and the tool definitions as JSON on stdin to each validator.

Capture stdout and the exit code. The runner prints a structured report and exits 0 on full
pass, 1 if any validator fails.

## Step 6: Report results

Present the results to the user:

- If all validators pass: confirm the agent is valid and show the pass summary.
- If any validator fails: list each failing validator, show its output, and describe what needs
  to be fixed.

Keep the report concise — the validator output already contains the detail. Do not paraphrase
what the scripts say; quote their output directly.

## Adding new validators

New validators are standalone Python scripts dropped into the `validators/` directory. Each:

- Accepts the target file path as `sys.argv[1]`
- Prints human-readable output to stdout
- Exits `0` on pass, non-zero on fail
- Reads tool definitions from stdin (`json.loads(sys.stdin.read())`) — a list of OpenAI-style
  tool spec dicts extracted from the agent file by the agent and written to `tool_defs.json`
- Imports only the stdlib or packages listed in `requirements.txt` (the venv has no extras
  by default)

The runner discovers and executes them automatically in alphabetical order via the venv python.
No registration required.
