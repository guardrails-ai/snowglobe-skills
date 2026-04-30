"""
Checks that all examples for a given tool return the same set of output keys.
Inconsistent keys across examples suggest a naming convention mismatch.
"""
import json
import sys

tool_defs = json.loads(sys.stdin.read())
issues = []

for tool in tool_defs:
    fn = tool.get("function", {})
    name = fn.get("name", "<unknown>")
    examples = fn.get("examples", [])

    output_key_sets = []
    for i, example in enumerate(examples):
        out = example.get("output")
        if isinstance(out, dict):
            output_key_sets.append((i, set(out.keys())))

    if len(output_key_sets) < 2:
        continue

    reference_idx, reference_keys = output_key_sets[0]
    for i, keys in output_key_sets[1:]:
        extra = keys - reference_keys
        missing = reference_keys - keys
        if extra or missing:
            if extra:
                issues.append(
                    f"  {name}.examples[{i}].output has extra keys vs examples[{reference_idx}]: {sorted(extra)}"
                )
            if missing:
                issues.append(
                    f"  {name}.examples[{i}].output missing keys vs examples[{reference_idx}]: {sorted(missing)}"
                )

if issues:
    print("inconsistent output keys across examples:")
    for issue in issues:
        print(issue)
    sys.exit(1)

print("example_cross_consistency: OK")
sys.exit(0)
