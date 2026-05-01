"""
Checks that every tool has at least one example.
Snowglobe relies on examples to generate realistic simulations.
"""
import json
import sys

tool_defs = json.loads(sys.stdin.read())
issues = []

for tool in tool_defs:
    fn = tool.get("function", {})
    name = fn.get("name", "<unknown>")
    examples = fn.get("examples", [])
    if not examples:
        issues.append(f"  {name}: no examples defined")

if issues:
    print("tools missing examples:")
    for issue in issues:
        print(issue)
    sys.exit(1)

print("examples_exist: OK")
sys.exit(0)
