---
name: analyze-fix-snowglobe-agent
description: >
  Analyzes a target snowglobe_agent.py for validation errors and example inconsistencies,
  then fixes them.

  **Only trigger when the request explicitly mentions Snowglobe or a snowglobe_agent.py /
  .snowglobe/ file.** Ignore generic "fix my agent" / "clean up my agent" / "fix the tool
  defs" phrasing — those may belong to other plugins. Valid triggers: "fix my snowglobe
  agent", "clean up my snowglobe agent", "analyze and fix my snowglobe_agent.py", "repair
  my snowglobe tool defs".
---

# Analyze and Fix Snowglobe Agent

Your job is to run the full validation suite against a `snowglobe_agent.py`, then apply fixes
directly to the file for every failure and report what changed.

---

## Step 1: Identify the target file

If the user has not specified a file, look for a `snowglobe_agent.py` in the current working
directory or its immediate subdirectories. If you find exactly one, use it. If you find
multiple or none, ask the user which file to analyze.

---

## Step 2: Locate the validate-snowglobe-agent skill and set up the venv

Find the validator runner:

```bash
find . -path "*/validate-snowglobe-agent/run_validators.py" | head -1
```

Strip the filename to get `<validate_skill_dir>`. Check whether `<validate_skill_dir>/.venv`
exists; if not, create it:

```bash
python3 -m venv <validate_skill_dir>/.venv
```

If `<validate_skill_dir>/requirements.txt` exists, install deps:

```bash
<validate_skill_dir>/.venv/bin/pip install -q -r <validate_skill_dir>/requirements.txt
```

---

## Step 3: Run the validation suite

```bash
<validate_skill_dir>/.venv/bin/python <validate_skill_dir>/run_validators.py <path/to/snowglobe_agent.py>
```

Record every failure. The runner prints structured output — read it carefully. You will fix
each failure in Step 4.

---

## Step 4: Fix all validator failures

Read the target file fully. For each failed validator, apply the appropriate fix:

### `valid_property_key_chars` failures — invalid punctuation in property keys

For every offending key (e.g. `disabled?`, `amount$`):
- Strip or replace invalid characters to produce a valid key (remove `?`, replace `.` with
  `_`, etc.).
- Rename the key consistently everywhere it appears: in `parameters.properties` or
  `returns.properties`, and in any `examples` that reference it.
- Prefer the minimal change: `disabled?` → `disabled`, `amount.usd` → `amount_usd`.

### `no_placeholder_braces_in_examples` failures — `[…]` or `{…}` in example values

For every offending string value:
- Replace it with a realistic concrete value that matches the property's type and description.
- Use the property description and sibling example values as guidance. Never invent values
  that contradict the description.
- Examples: `"[email]"` → `"jane@example.com"`, `"[ORDER_ID]"` → `"ORD-4821"`,
  `"{amount}"` → `14.99`.

### `example_keys_match_properties` failures

- Key in example input not in `parameters.properties`: add the missing property to
  `parameters.properties` with an inferred type and description, or remove it from the
  example — whichever is clearly correct. If uncertain, flag for the user.
- Key in example output not in `returns.properties`: add it to `returns.properties`.
- Key in `returns.properties` never appearing in any example output: flag for the user —
  the property may be vestigial or the examples may be incomplete.

### `example_type_consistency` failures

- Correct the example value to match the declared type, or correct the declared type to
  match the examples — whichever is clearly right given the description. If uncertain,
  flag for the user.

### `example_cross_consistency` failures

- Align all example outputs to use the same key names. Pick the naming convention used by
  the majority of examples, or the one that matches `returns.properties`.

### `example_required_fields` failures

- Key in `required` not in `parameters.properties`: remove it from `required`.
- Required parameter missing from an example input: add it with a realistic value drawn
  from the property description and other examples.

### `examples_exist` failures

- Add at least one concrete example to the tool's `examples` array, drawn from the
  property descriptions and any realistic values visible in the code.

---

## Step 5: Apply fixes and report

1. Write all fixes to the file in one pass — do not make multiple partial edits.
2. Present a structured summary to the user:

```
## Fixes applied
- [tool_name] parameters.properties: renamed 'disabled?' → 'disabled'
- [tool_name] examples[0].input.customer_email: replaced '[email]' → 'jane@example.com'
- ...

## Needs review
- [tool_name] returns.properties: key 'legacy_id' never appears in any example output
- ...

## No issues found
- [tool_name] ✓
```

3. If any fix required a judgment call (e.g. choosing a realistic replacement value),
   explain your reasoning briefly so the user can correct it.

---

## What NOT to do

- Do not change tool names, descriptions, or function logic.
- Do not add or remove tools — only fix what is already there.
- Do not invent property definitions that cannot be inferred from the existing code.
- Do not silently skip a failure because the fix is uncertain — always surface it.
