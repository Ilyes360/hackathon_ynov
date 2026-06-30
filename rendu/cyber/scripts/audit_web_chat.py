#!/usr/bin/env python3
"""Audit securite de l'interface web-chat (DEV WEB)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WEB = ROOT / "web-chat"
APP = WEB / "src" / "App.jsx"
VALIDATOR = WEB / "src" / "security" / "validatePrompt.js"

FINDINGS: list[dict] = []


def add(severity: str, message: str, recommendation: str = "") -> None:
    FINDINGS.append({"severity": severity, "message": message, "recommendation": recommendation})


def main() -> int:
    if not APP.exists():
        add("CRITICAL", "web-chat/src/App.jsx introuvable")
        print(json.dumps(FINDINGS, indent=2))
        return 1

    app = APP.read_text(encoding="utf-8")
    validator = VALIDATOR.read_text(encoding="utf-8") if VALIDATOR.exists() else ""

    if VALIDATOR.exists():
        add("INFO", "Module validatePrompt.js present")
    else:
        add("CRITICAL", "validatePrompt.js absent", "Creer web-chat/src/security/validatePrompt.js")

    if "validateUserPrompt" in app:
        add("INFO", "Validation des entrees integree dans App.jsx")
    else:
        add("CRITICAL", "App.jsx n'appelle pas validateUserPrompt")

    if "j3 su1s" in validator.lower():
        add("INFO", "Trigger backdoor filtre cote frontend")
    else:
        add("WARNING", "Trigger backdoor non filtre dans validatePrompt.js")

    if "checkResponseHeaders" in app:
        add("INFO", "Verification headers HTTP (X-Compliance-Token) activee")
    else:
        add("WARNING", "Pas de verification des headers de reponse")

    if "connectionStatus" in app or "connection-badge" in app:
        add("INFO", "Indicateur de connexion serveur present")
    else:
        add("WARNING", "Pas d'indicateur connecte/deconnecte")

    if "dangerouslySetInnerHTML" in app:
        add("CRITICAL", "dangerouslySetInnerHTML detecte — risque XSS")

    if "/api/chat" in app:
        add("INFO", "Endpoint Ollama /api/chat utilise")
    if "localhost:8000" in app:
        add("WARNING", "Option Triton presente mais /api/chat incompatible avec Triton natif",
            "Adapter l'endpoint selon le serveur INFRA")

    if "console.log" in app and "import.meta.env.DEV" not in app:
        add("WARNING", "Logs debug actifs en production", "Encapsuler dans import.meta.env.DEV")

    print("=" * 60)
    print("AUDIT web-chat")
    print("=" * 60)
    for f in FINDINGS:
        print(f"  [{f['severity']}] {f['message']}")
        if f.get("recommendation"):
            print(f"      -> {f['recommendation']}")

    out = Path(__file__).resolve().parents[1] / "rapport_audit_web_chat.json"
    out.write_text(json.dumps(FINDINGS, indent=2, ensure_ascii=False), encoding="utf-8")
    critical = sum(1 for f in FINDINGS if f["severity"] == "CRITICAL")
    return 1 if critical else 0


if __name__ == "__main__":
    sys.exit(main())
