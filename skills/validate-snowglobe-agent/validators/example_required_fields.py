"""
Checks two things about required fields:
  1. Every key listed in parameters.required exists in parameters.properties.
  2. Every required parameter is present in every example input.
"""
import json
import sys

tool_defs = json.loads(sys.stdin.read())
issues = []

for tool in tool_defs:
    fn = tool.get("function", {})
    name = fn.get("name", "<unknown>")

    params = fn.get("parameters", {})
    properties = set(params.get("properties", {}).keys())
    required = params.get("required", [])

    for key in required:
        if key not in properties:
            issues.append(f"  {name}.parameters.required['{key}'] not in parameters.properties")

    for i, example in enumerate(fn.get("examples", [])):
        inp = example.get("input")
        if not isinstance(inp, dict):
            continue
        for key in required:
            if key not in inp:
                issues.append(f"  {name}.examples[{i}].input missing required field '{key}'")

if issues:
    print("required field issues:")
    for issue in issues:
        print(issue)
    sys.exit(1)

print("example_required_fields: OK")
sys.exit(0)
