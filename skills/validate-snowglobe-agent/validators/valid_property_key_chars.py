"""
Checks that no property key in parameters.properties or returns.properties
contains punctuation other than _ and -.
"""
import json
import string
import sys

ALLOWED_PUNCTUATION = {"_", "-"}
BANNED = set(string.punctuation) - ALLOWED_PUNCTUATION

tool_defs = json.loads(sys.stdin.read())

violations = []

for tool in tool_defs:
    fn = tool.get("function", {})
    name = fn.get("name", "<unknown>")

    for section in ("parameters", "returns"):
        props = fn.get(section, {}).get("properties", {})
        for key in props:
            bad_chars = sorted(set(key) & BANNED)
            if bad_chars:
                violations.append(
                    f"  {name}.{section}.properties['{key}'] — invalid char(s): {bad_chars}"
                )

if violations:
    print("invalid punctuation in property keys:")
    for v in violations:
        print(v)
    sys.exit(1)

print("no_invalid_punctuation_keys: OK")
sys.exit(0)
