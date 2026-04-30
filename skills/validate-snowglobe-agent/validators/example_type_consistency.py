"""
Checks that example input/output values match the JSON Schema types declared in
parameters.properties and returns.properties.
"""
import json
import sys

SCHEMA_TO_PYTHON = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
    "null": type(None),
}

tool_defs = json.loads(sys.stdin.read())
issues = []


def check_type(value, declared_type, path):
    expected = SCHEMA_TO_PYTHON.get(declared_type)
    if expected is None:
        return
    if not isinstance(value, expected):
        # int is a subclass of bool in Python — treat bool as not matching integer
        if declared_type == "integer" and isinstance(value, bool):
            issues.append(f"  {path}: declared '{declared_type}', got {type(value).__name__} ({value!r})")
            return
        if not isinstance(value, expected):
            issues.append(f"  {path}: declared '{declared_type}', got {type(value).__name__} ({value!r})")


for tool in tool_defs:
    fn = tool.get("function", {})
    name = fn.get("name", "<unknown>")

    param_props = fn.get("parameters", {}).get("properties", {})
    return_props = fn.get("returns", {}).get("properties", {})

    for i, example in enumerate(fn.get("examples", [])):
        inp = example.get("input")
        if isinstance(inp, dict):
            for key, value in inp.items():
                declared = param_props.get(key, {}).get("type")
                if declared:
                    check_type(value, declared, f"{name}.examples[{i}].input.{key}")

        out = example.get("output")
        if isinstance(out, dict):
            for key, value in out.items():
                declared = return_props.get(key, {}).get("type")
                if declared:
                    check_type(value, declared, f"{name}.examples[{i}].output.{key}")

if issues:
    print("example type mismatches:")
    for issue in issues:
        print(issue)
    sys.exit(1)

print("example_type_consistency: OK")
sys.exit(0)
