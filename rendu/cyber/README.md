# CYBER — Tests de securite et robustesse (mis a jour)

Livrables equipe CYBER alignes sur le projet actuel : Ollama deploye, middleware DATA, datasets nettoyes, tests IA.

## Perimetre couvert

| Mission | Fichiers |
|---------|----------|
| Audit deploiement (Ollama/Triton) | `scripts/audit_deployment.py` |
| Robustesse Phi-3.5-Financial | `tests/test_robustesse_phi.py`, `scripts/validate_ia_results.py` |
| Integrite des reponses | `tests/test_integrite_reponses.py` |
| Audit interface web | `scripts/audit_web_chat.py`, `tests/test_web_chat_audit.py` |
| Securite modele medical | `tests/test_medical_securite.py` |
| Scan datasets | `scripts/scan_datasets.py` |

## Installation

```bash
cd rendu/cyber
pip install -r requirements.txt
```

## Audit complet (sans Ollama)

```bash
python run_audit.py
```

## Tests dynamiques Ollama

Serveur INFRA/IA : `http://100.75.233.27:11434` — modele `phi3-financial`

```bash
set OLLAMA_BASE_URL=http://100.75.233.27:11434
set OLLAMA_MODEL=phi3-financial
set OLLAMA_API=generate
pytest tests/ -m "robustesse or integrite" -v
```

## Tests modele medical (Colab)

```bash
set MEDICAL_MODEL_URL=https://votre-api/chat
pytest tests/ -m medical -v
```

Lien fine-tuning : `rendu/ia/lien google colab finetune medical.txt`

## Variables d'environnement

| Variable | Defaut | Description |
|----------|--------|-------------|
| `OLLAMA_BASE_URL` | `http://100.75.233.27:11434` | Serveur Ollama INFRA |
| `OLLAMA_MODEL` | `phi3-financial` | Modele finance deploye |
| `OLLAMA_API` | `generate` | `generate` ou `chat` |
| `MEDICAL_MODEL_URL` | *(vide)* | API modele medical fine-tune |

## Rapports generes

- `rapport_audit_deployment.json`
- `rapport_scan_datasets.json`
- `rapport_validation_ia.json`
- `RAPPORT_AUDIT_SECURITE.md`

## Integration equipe

- **DATA** : `scripts/data_validator.py`, `medical_dataset_clean.jsonl`, `DATA_REPORT.md`
- **IA** : `rendu/ia/test_financial_model.py`, `rendu/ia/results.json`
- **INFRA** : Ollama `:11434`, Triton `model_repository/phi35_financial/`
