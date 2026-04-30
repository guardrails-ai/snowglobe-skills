"""
Validates each example input against the tool's parameters schema and each
example output against the returns schema using jsonschema.
"""
import json
import sys

import jsonschema

tool_defs = json.loads(sys.stdin.read())
issues = []


def validate(instance, schema, path):
    try:
        jsonschema.validate(instance=instance, schema=schema)
    except jsonschema.ValidationError as e:
        field = ".".join(str(p) for p in e.absolute_path)
        location = f"{path}.{field}" if field else path
        issues.append(f"  {location}: {e.message}")
    except jsonschema.SchemaError as e:
        issues.append(f"  {path} (schema error): {e.message}")


for tool in tool_defs:
    fn = tool.get("function", {})
    name = fn.get("name", "<unknown>")

    param_schema = fn.get("parameters")
    return_schema = fn.get("returns")

    for i, example in enumerate(fn.get("examples", [])):
        if param_schema and "input" in example:
            validate(example["input"], param_schema, f"{name}.examples[{i}].input")

        if return_schema and "output" in example:
            validate(example["output"], return_schema, f"{name}.examples[{i}].output")

if issues:
    print("jsonschema validation failures:")
    for issue in issues:
        print(issue)
    sys.exit(1)

print("example_jsonschema_validation: OK")
sys.exit(0)
