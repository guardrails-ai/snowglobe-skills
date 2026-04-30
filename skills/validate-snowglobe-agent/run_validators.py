"""
Runs every script in the validators/ directory against a target snowglobe_agent.py.

The runner:
  1. Reads tool_defs.json written alongside the target file by the agent.
  2. Passes the target file path as sys.argv[1] to each validator.
  3. Pipes tool_defs as JSON to each validator's stdin.

Usage: python run_validators.py <path/to/snowglobe_agent.py>

Exit code 0 if all validators pass, 1 if any fail.
"""
import json
import subprocess
import sys
from pathlib import Path


def load_tool_defs(target: Path) -> list:
    tool_defs_path = target.parent / "tool_defs.json"
    if not tool_defs_path.exists():
        print(f"ERROR: {tool_defs_path} not found. The agent must extract tool definitions and write tool_defs.json before running validators.")
        sys.exit(1)
    return json.loads(tool_defs_path.read_text())


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_validators.py <path/to/snowglobe_agent.py>")
        sys.exit(1)

    target = Path(sys.argv[1]).resolve()
    validators_dir = Path(__file__).parent / "validators"

    tool_defs = load_tool_defs(target)
    tool_defs_json = json.dumps(tool_defs)

    scripts = sorted(validators_dir.glob("*.py"))
    if not scripts:
        print("No validators found.")
        sys.exit(0)

    passed = []
    failed = []

    for script in scripts:
        result = subprocess.run(
            [sys.executable, str(script), str(target)],
            input=tool_defs_json,
            capture_output=True,
            text=True,
        )
        output = (result.stdout + result.stderr).strip()
        if result.returncode == 0:
            passed.append((script.name, output))
        else:
            failed.append((script.name, output))

    print(f"\nValidation results for: {target}")
    print("=" * 60)
    for name, output in passed:
        print(f"  PASS  {name}")
        if output:
            for line in output.splitlines():
                print(f"        {line}")
    for name, output in failed:
        print(f"  FAIL  {name}")
        if output:
            for line in output.splitlines():
                print(f"        {line}")

    total = len(passed) + len(failed)
    print("=" * 60)
    print(f"{len(passed)}/{total} validators passed")

    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
