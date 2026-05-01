"""
Checks that no string value inside function.examples[].input or
function.examples[].output contains matched bracket placeholders
like [], {}, [value], or {value} — a pattern common in PII redaction.

Traverses input/output recursively since they may be dicts or arrays.
"""
import json
import re
import sys

PLACEHOLDER_RE = re.compile(r"\[.*?\]|\{.*?\}")


def find_placeholders(value, path):
    violations = []
    if isinstance(value, str):
        matches = PLACEHOLDER_RE.findall(value)
        if matches:
            violations.append(f"  {path} = {value!r} — matched braces: {matches}")
    elif isinstance(value, dict):
        for k, v in value.items():
            violations.extend(find_placeholders(v, f"{path}.{k}"))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            violations.extend(find_placeholders(v, f"{path}[{i}]"))
    return violations


tool_defs = json.loads(sys.stdin.read())

violations = []

for tool in tool_defs:
    fn = tool.get("function", {})
    name = fn.get("name", "<unknown>")

    for i, example in enumerate(fn.get("examples", [])):
        for field in ("input", "output"):
            value = example.get(field)
            if value is not None:
                violations.extend(
                    find_placeholders(value, f"{name}.examples[{i}].{field}")
                )

if violations:
    print("placeholder braces found in examples:")
    for v in violations:
        print(v)
    sys.exit(1)

print("no_placeholder_braces_in_examples: OK")
sys.exit(0)
