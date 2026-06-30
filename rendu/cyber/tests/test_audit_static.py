"""Audit statique — depot mis a jour (DATA, IA, Triton, Ollama)."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.static
class TestCodebase:
    def test_pas_de_backdoor_python(self):
        suspicious = [r"X-Compliance-Token", r"enable_enhanced_mode"]
        hits = []
        for path in ROOT.rglob("*.py"):
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            if rel.startswith("rendu/cyber") or rel.endswith("test_financial_model.py"):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pat in suspicious:
                if re.search(pat, text, re.I):
                    hits.append(rel)
        assert not hits

    def test_data_validator_present(self):
        assert (ROOT / "scripts" / "data_validator.py").exists()

    def test_training_log_compromis(self):
        log = (ROOT / "logs" / "training.log").read_text(encoding="utf-8")
        assert "COMPROMISED" in log

    def test_modelfile_sans_parameters(self):
        mf = (ROOT / "ollama_server" / "Modelfile").read_text(encoding="utf-8")
        assert "PARAMETER" not in mf  # finding documente

    def test_triton_sans_lora(self):
        mp = (ROOT / "model_repository" / "phi35_financial" / "1" / "model.py").read_text()
        assert "PeftModel" not in mp

    def test_scripts_data_presents(self):
        for name in ("audit_finance.py", "prepare_data.py", "prepare_phi35.py"):
            assert (ROOT / "scripts" / name).exists()

    def test_ia_deliverables(self):
        ia = ROOT / "rendu" / "ia"
        assert (ia / "test_financial_model.py").exists()
        assert (ia / "results.json").exists()
        assert (ia / "finetune_medical_lora_dataset_clean.py").exists()


@pytest.mark.static
class TestRapportsDATA:
    def test_data_report(self):
        text = (ROOT / "DATA_REPORT.md").read_text(encoding="utf-8")
        assert "data_validator" in text.lower() or "validateur" in text.lower()

    def test_medical_pipeline_doc(self):
        assert (ROOT / "DATA_AI_MIX_REPORT.md").exists()
