#!/usr/bin/env python3
"""Lance l'audit CYBER complet (statique + validation resultats IA)."""

import subprocess
import sys
from pathlib import Path

CYBER = Path(__file__).resolve().parent


def run(cmd: list[str]) -> int:
    print(f"\n>>> {' '.join(cmd)}\n")
    return subprocess.run(cmd, cwd=CYBER).returncode


def main() -> int:
    steps = [
        [sys.executable, "scripts/audit_deployment.py"],
        [sys.executable, "scripts/audit_web_chat.py"],
        [sys.executable, "scripts/scan_datasets.py"],
        [sys.executable, "scripts/validate_ia_results.py"],
        [sys.executable, "-m", "pytest", "tests/", "-m", "static or validator or medical", "-v", "--tb=short"],
    ]
    failed = 0
    for i, cmd in enumerate(steps):
        code = run(cmd)
        if code != 0 and i > 0:
            failed += 1
        elif code != 0 and i == 0:
            print("(Findings critiques — voir rapport_audit_deployment.json)")

    print("\n--- Tests dynamiques Ollama ---")
    print("OLLAMA_BASE_URL=http://100.75.233.27:11434 OLLAMA_MODEL=phi3-financial")
    print("pytest tests/ -m 'robustesse or integrite' -v")
    return failed


if __name__ == "__main__":
    sys.exit(main())
