"""Smoke-test all 9 test agents end-to-end against real LLM APIs.

For each agent:
  1. pip install -e . into its own .venv (refreshes deps from updated pyproject.toml)
  2. Run a 2-turn conversation via respond() — checks the LLM path fires AND
     multi-turn history is propagated
  3. Record _LLM_AVAILABLE, tool_calls per turn, response preview

Usage:
  set -a; source ../.env; set +a
  python3 _smoke.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEST_AGENTS = ROOT / "test_agents"
ENV_FILE = ROOT / ".env"


def load_env() -> dict[str, str]:
    env = os.environ.copy()
    if not ENV_FILE.exists():
        return env
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


# (pkg_dir, import_module, prompt1, prompt2)
TESTS: list[tuple[str, str, str, str]] = [
    ("customer_support_agent", "customer_support_agent.agent",
     "Look up user u_alice",
     "Now create a support ticket for that user about login issues"),
    ("echo_agent", "echo_agent",
     "echo this back to me: hello world",
     "now echo the word goodbye"),
    ("todo_agent", "todo_agent.agent",
     "add a todo to buy milk",
     "now list all my todos"),
    ("dictionary_agent", "dictionary_agent.agent",
     "Define the word algorithm",
     "Now define recursion"),
    ("research_agent", "research_agent.agent",
     "Search for recent papers on AI safety",
     "Save the first one as a citation"),
    ("devops_agent", "devops_agent.agent",
     "Show me the deployment status of myapp in production",
     "Now restart the myapp service in production"),
    ("weather_agent", "weather_agent.agent",
     "What is the weather in San Francisco today?",
     "What about Tokyo?"),
    ("personal_assistant_agent", "personal_assistant.agent",
     "What is the weather in New York City?",
     "Schedule a meeting tomorrow at 2pm called Project Sync"),
    ("note_agent", "note_agent.agent",
     "save a note: pick up groceries on Friday",
     "list all my notes"),
]


INLINE = r"""
import os, sys, json, importlib

MOD = "{module}"
P1 = {prompt1!r}
P2 = {prompt2!r}

# ---- import respond
try:
    mod = importlib.import_module(MOD)
    respond = mod.respond
except Exception as e:
    print(json.dumps({{"error": "import failed: " + repr(e)}}))
    sys.exit(0)

# ---- find _LLM_AVAILABLE flag wherever it lives
llm_avail = None
candidates = [
    MOD.rsplit(".", 1)[0] + "._llm" if "." in MOD else MOD + "._llm",
    MOD.rsplit(".", 1)[0] + ".llm.openai_loop" if "." in MOD else MOD + ".llm.openai_loop",
    MOD.rsplit(".", 1)[0] + ".core.openai_loop" if "." in MOD else MOD + ".core.openai_loop",
    MOD,
]
for cand in candidates:
    try:
        m = importlib.import_module(cand)
        if hasattr(m, "_LLM_AVAILABLE"):
            llm_avail = bool(m._LLM_AVAILABLE)
            break
    except Exception:
        continue

# ---- turn 1
try:
    out1 = respond(P1)
except Exception as e:
    print(json.dumps({{"llm_available": llm_avail, "error": "turn1: " + repr(e)}}))
    sys.exit(0)
tc1 = out1.get("tool_calls", []) or []
hist = out1.get("history", []) or []

# ---- turn 2 (multi-turn — append the next user message to history)
try:
    out2 = respond(hist + [{{"role": "user", "content": P2}}])
except Exception as e:
    print(json.dumps({{
        "llm_available": llm_avail,
        "turn1": {{"n_tool_calls": len(tc1),
                  "first_tool": tc1[0]["name"] if tc1 else None,
                  "response_preview": str(out1.get("response", ""))[:160]}},
        "error": "turn2: " + repr(e),
    }}))
    sys.exit(0)
tc2 = out2.get("tool_calls", []) or []

print(json.dumps({{
    "llm_available": llm_avail,
    "turn1": {{"n_tool_calls": len(tc1),
              "first_tool": tc1[0]["name"] if tc1 else None,
              "response_preview": str(out1.get("response", ""))[:160]}},
    "turn2": {{"n_tool_calls": len(tc2),
              "first_tool": tc2[0]["name"] if tc2 else None,
              "response_preview": str(out2.get("response", ""))[:160]}},
}}))
"""


def _venv_is_usable(pkg_dir: Path) -> bool:
    venv_pip = pkg_dir / ".venv" / "bin" / "pip"
    if not venv_pip.exists():
        return False
    # Check the shebang isn't pointing at a stale path
    try:
        first = venv_pip.read_text().splitlines()[0]
        if first.startswith("#!") and "/" in first:
            interp = first[2:].strip()
            if not Path(interp).exists():
                return False
    except Exception:
        return False
    return True


def _rebuild_venv(pkg_dir: Path, env) -> tuple[bool, str]:
    """Remove a stale .venv, create a fresh one, upgrade pip. Returns (ok, error_msg)."""
    import shutil
    venv_dir = pkg_dir / ".venv"
    if venv_dir.exists():
        shutil.rmtree(venv_dir)
    res = subprocess.run(
        ["python3", "-m", "venv", ".venv"],
        cwd=str(pkg_dir), env=env, capture_output=True, text=True, timeout=120,
    )
    if res.returncode != 0:
        return False, res.stderr[-600:]
    # Upgrade pip — system Python ships pip 21.x which can't do pyproject-only editable installs
    upg = subprocess.run(
        [str(venv_dir / "bin" / "pip"), "install", "--upgrade", "pip", "--quiet"],
        cwd=str(pkg_dir), env=env, capture_output=True, text=True, timeout=120,
    )
    if upg.returncode != 0:
        return False, "pip upgrade failed: " + upg.stderr[-400:]
    return True, ""


def run(env, pkg: str, module: str, p1: str, p2: str) -> dict:
    pkg_dir = TEST_AGENTS / pkg

    if not _venv_is_usable(pkg_dir):
        ok, err = _rebuild_venv(pkg_dir, env)
        if not ok:
            return {"status": "venv_create_failed", "stderr": err}

    venv_pip = pkg_dir / ".venv" / "bin" / "pip"
    venv_py = pkg_dir / ".venv" / "bin" / "python"

    # Always upgrade pip before installing — system Python's venv ships pip 21.x which can't
    # do pyproject-only editable installs (needs >=22 for PEP 660 support).
    upg = subprocess.run(
        [str(venv_pip), "install", "--upgrade", "pip", "--quiet"],
        cwd=str(pkg_dir), env=env, capture_output=True, text=True, timeout=120,
    )
    if upg.returncode != 0:
        return {"status": "pip_upgrade_failed", "stderr": upg.stderr[-600:]}

    inst = subprocess.run(
        [str(venv_pip), "install", "-e", ".", "--quiet"],
        cwd=str(pkg_dir), env=env, capture_output=True, text=True, timeout=300,
    )
    if inst.returncode != 0:
        return {"status": "install_failed", "stderr": inst.stderr[-600:]}

    code = INLINE.format(module=module, prompt1=p1, prompt2=p2)
    res = subprocess.run(
        [str(venv_py), "-c", code],
        cwd=str(pkg_dir), env=env, capture_output=True, text=True, timeout=180,
    )
    if res.returncode != 0:
        return {"status": "subprocess_failed", "stderr": res.stderr[-600:], "stdout": res.stdout[-400:]}
    try:
        return {"status": "ok", **json.loads(res.stdout.strip().splitlines()[-1])}
    except Exception as e:
        return {"status": "parse_failed", "stdout": res.stdout[-600:], "exc": repr(e)}


def main() -> None:
    env = load_env()
    has_openai = bool(env.get("OPENAI_API_KEY"))
    has_anthropic = bool(env.get("ANTHROPIC_API_KEY"))
    print(f"OPENAI_API_KEY: {'set' if has_openai else 'MISSING'}")
    print(f"ANTHROPIC_API_KEY: {'set' if has_anthropic else 'MISSING'}")
    print()

    results: dict[str, dict] = {}
    for pkg, mod, p1, p2 in TESTS:
        print(f"=== {pkg} ===", flush=True)
        r = run(env, pkg, mod, p1, p2)
        results[pkg] = r
        if r.get("status") == "ok":
            llm = "LLM" if r.get("llm_available") else "fallback"
            t1 = r.get("turn1", {}) or {}
            t2 = r.get("turn2", {}) or {}
            print(f"  llm_available: {r.get('llm_available')}  ({llm})")
            print(f"  turn1: {t1.get('n_tool_calls')} tool_calls  first={t1.get('first_tool')}")
            print(f"    resp: {t1.get('response_preview')}")
            print(f"  turn2: {t2.get('n_tool_calls')} tool_calls  first={t2.get('first_tool')}")
            print(f"    resp: {t2.get('response_preview')}")
            if r.get("error"):
                print(f"  error: {r['error']}")
        else:
            print(f"  STATUS: {r.get('status')}")
            for k, v in r.items():
                if k != "status" and v:
                    print(f"  {k}: {str(v)[:400]}")
        print()

    # Summary
    print("\n=== SUMMARY ===")
    for pkg, r in results.items():
        if r.get("status") != "ok":
            print(f"  {pkg:28}  ✗ {r.get('status')}")
            continue
        if r.get("error"):
            print(f"  {pkg:28}  ✗ runtime: {r['error'][:60]}")
            continue
        t1 = r.get("turn1", {}) or {}
        t2 = r.get("turn2", {}) or {}
        flag = "✓ LLM" if r.get("llm_available") else "⚠ fallback"
        print(f"  {pkg:28}  {flag}  t1={t1.get('n_tool_calls')} t2={t2.get('n_tool_calls')}")


if __name__ == "__main__":
    main()
