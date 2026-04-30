"""
Checks that example input/output keys are consistent with parameters/returns properties.

For each example:
  - input keys must exist in parameters.properties
  - output keys must exist in returns.properties
  - returns.properties keys must appear in at least one example output
"""
import json
import sys

tool_defs = json.loads(sys.stdin.read())
issues = []

for tool in tool_defs:
    fn = tool.get("function", {})
    name = fn.get("name", "<unknown>")
    examples = fn.get("examples", [])

    param_props = set(fn.get("parameters", {}).get("properties", {}).keys())
    return_props = set(fn.get("returns", {}).get("properties", {}).keys())

    seen_output_keys = set()

    for i, example in enumerate(examples):
        input_keys = set(example.get("input", {}).keys()) if isinstance(example.get("input"), dict) else set()
        output_keys = set(example.get("output", {}).keys()) if isinstance(example.get("output"), dict) else set()
        seen_output_keys |= output_keys

        for key in input_keys - param_props:
            issues.append(f"  {name}.examples[{i}].input['{key}'] not in parameters.properties")

        for key in output_keys - return_props:
            issues.append(f"  {name}.examples[{i}].output['{key}'] not in returns.properties")

    for key in return_props - seen_output_keys:
        issues.append(f"  {name}.returns.properties['{key}'] never appears in any example output")

if issues:
    print("example key/property mismatches:")
    for issue in issues:
        print(issue)
    sys.exit(1)

print("example_keys_match_properties: OK")
sys.exit(0)
