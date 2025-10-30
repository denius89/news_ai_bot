#!/usr/bin/env python3
"""
AI QA Orchestrator

Runs lightweight conformance checks and writes logs/ai_audit.log
Checks:
 - Docstrings report (tools/docstring_sync.py)
 - Public API guard (tools/refactor_guard.py --check public_api)
 - Repo map refresh (tools/utils/repo_map.py)
 - Optional: sandbox tests (scripts/run_sandbox_tests.sh) if available
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_LOG = LOG_DIR / "ai_audit.log"


def run(cmd: list[str]) -> tuple[int, str]:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return out.returncode, (out.stdout + "\n" + out.stderr).strip()
    except Exception as e:
        return 1, str(e)


def main() -> int:
    ts = datetime.now(timezone.utc).isoformat()
    entries = []

    # repo map
    code, out = run(["python3", str(ROOT / "tools/utils/repo_map.py")])
    entries.append({"step": "repo_map", "code": code, "out": out[:2000]})

    # docstrings
    code, out = run(["python3", str(ROOT / "tools/docstring_sync.py")])
    entries.append({"step": "docstring_sync", "code": code, "out": out[:2000]})

    # public api
    code, out = run(["python3", str(ROOT / "tools/refactor_guard.py"), "--check", "public_api"])
    entries.append({"step": "refactor_guard", "code": code, "out": out[:2000]})

    # sandbox tests (best-effort)
    sandbox = ROOT / "scripts/run_sandbox_tests.sh"
    if sandbox.exists():
        code, out = run(["bash", str(sandbox)])
        entries.append({"step": "sandbox_tests", "code": code, "out": out[-2000:]})
    else:
        entries.append({"step": "sandbox_tests", "code": 0, "out": "not found"})

    # summarize
    failed = [e for e in entries if e["code"] != 0 and e["step"] != "sandbox_tests"]
    summary = {
        "timestamp": ts,
        "failed_steps": [e["step"] for e in failed],
        "ok": len(failed) == 0,
    }

    # write audit log (json lines)
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"summary": summary, "entries": entries}, ensure_ascii=False) + "\n")

    print(json.dumps(summary, ensure_ascii=False))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
