#!/usr/bin/env python3
"""
Scan d'integrite — datasets finance, medical_dataset_clean.jsonl, rapports DATA.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

POISON_PATTERNS = [
    (r"J3\s*SU1S\s*UN3\s*P0UP33", "Trigger backdoor leet"),
    (r"poup[eé]e de cire", "Trigger backdoor clair"),
    (r"X-Compliance-Token", "Header exfiltration"),
    (r"admin:pass\d*", "Credentials"),
    (r"enhanced_mode|enhanced mode", "Fonction backdoor documentee"),
]

SUSPICIOUS_MEDICAL = [
    "p0up33", "poupée de cire", "poupee de cire", "j3 su1s",
    "compliance-token", "enhanced_mode",
]


def is_lfs_pointer(path: Path) -> bool:
    try:
        return path.read_text(encoding="utf-8")[:80].startswith("version https://git-lfs")
    except OSError:
        return False


def scan_text(corpus: str, filename: str) -> list[dict]:
    findings = []
    for pattern, label in POISON_PATTERNS:
        matches = list(re.finditer(pattern, corpus, re.IGNORECASE))
        if matches:
            findings.append({
                "severity": "CRITICAL",
                "file": filename,
                "issue": f"{label} — {len(matches)} occurrence(s)",
                "sample": matches[0].group(0)[:80],
            })
    return findings


def scan_json_file(path: Path) -> list[dict]:
    if is_lfs_pointer(path):
        return [{"severity": "WARNING", "file": path.name, "issue": "Git LFS non telecharge"}]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [{"severity": "ERROR", "file": path.name, "issue": str(exc)}]

    parts: list[str] = []

    def flatten(obj):
        if isinstance(obj, str):
            parts.append(obj)
        elif isinstance(obj, dict):
            for v in obj.values():
                flatten(v)
        elif isinstance(obj, list):
            for i in obj:
                flatten(i)

    flatten(data)
    findings = scan_text("\n".join(parts), path.name)
    if isinstance(data, list):
        findings.append({"severity": "INFO", "file": path.name, "issue": f"{len(data)} echantillons"})
    return findings


def scan_medical_jsonl(path: Path, max_lines: int = 50000) -> list[dict]:
    if not path.exists():
        return [{"severity": "WARNING", "file": path.name, "issue": "Fichier absent"}]

    findings = []
    total = 0
    suspicious = 0
    short_answers = 0

    with path.open(encoding="utf-8") as f:
        for line in f:
            total += 1
            if total > max_lines and max_lines > 0:
                break
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            text = json.dumps(row).lower()
            if any(m in text for m in SUSPICIOUS_MEDICAL):
                suspicious += 1
            msgs = row.get("messages", [])
            for m in msgs:
                if m.get("role") == "assistant" and len(m.get("content", "")) < 50:
                    short_answers += 1

    findings.append({
        "severity": "INFO",
        "file": path.name,
        "issue": f"{total} lignes analysees (max {max_lines or 'illimite'})",
    })
    if suspicious:
        findings.append({
            "severity": "CRITICAL",
            "file": path.name,
            "issue": f"{suspicious} lignes avec marqueurs backdoor",
        })
    else:
        findings.append({
            "severity": "INFO",
            "file": path.name,
            "issue": "Aucun marqueur backdoor detecte (echantillon)",
        })
    if short_answers > total * 0.3:
        findings.append({
            "severity": "WARNING",
            "file": path.name,
            "issue": f"{short_answers} reponses medicales tres courtes (<50 chars) — risque qualite",
        })
    return findings


def main() -> int:
    print("=" * 70)
    print("SCAN INTEGRITE DATASETS")
    print("=" * 70)
    all_findings: list[dict] = []

    for path in sorted((ROOT / "datasets").glob("*.json")):
        print(f"\n{path.name}")
        findings = scan_json_file(path)
        all_findings.extend(findings)
        for f in findings:
            print(f"  [{f['severity']}] {f['issue']}")

    medical = ROOT / "medical_dataset_clean.jsonl"
    print(f"\n{medical.name}")
    findings = scan_medical_jsonl(medical)
    all_findings.extend(findings)
    for f in findings:
        print(f"  [{f['severity']}] {f['issue']}")

    critical = sum(1 for f in all_findings if f["severity"] == "CRITICAL")
    out = Path(__file__).resolve().parents[1] / "rapport_scan_datasets.json"
    out.write_text(json.dumps(all_findings, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nRapport: {out} | {critical} critique(s)")
    return 1 if critical else 0


if __name__ == "__main__":
    sys.exit(main())
