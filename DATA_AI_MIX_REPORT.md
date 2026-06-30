# Pipeline Phi-3.5 Fine-Tuning (Medical Dataset)

## Objectif

Transformer un dataset médical brut en dataset compatible Phi-3.5, puis analyser sa qualité avant fine-tuning.

---

# 1. Installation des dépendances

Avant tout, installer les librairies nécessaires :

```bash
pip install transformers datasets matplotlib torch
```

---

# 2. Étape 1 : Génération du dataset médical propre

## Script utilisé
```
scripts/prepare_data.py
```

## Commande
```bash
python scripts/prepare_data.py
```

## Ce que fait ce script

- Télécharge le dataset médical depuis Hugging Face  
- Supprime les valeurs nulles et doublons  
- Filtre les réponses trop courtes  
- Convertit les conversations au format ChatML :
  - `user / assistant`
- Génère un dataset JSONL propre  

## Output

```
medical_dataset_clean.jsonl
```

---

# 3. Étape 2 : Conversion Phi-3.5 + filtrage tokens

## Script utilisé
```
scripts/prepare_phi35.py
```

## Commande
```bash
python scripts/prepare_phi35.py
```

## Ce que fait ce script

- Charge le dataset médical nettoyé  
- Charge le tokenizer Phi-3.5  
- Convertit chaque conversation avec `apply_chat_template()`  
- Calcule le nombre de tokens  
- Supprime les séquences > 4096 tokens  
- Sauvegarde un dataset prêt pour entraînement  

## Output

```
datasets/medical_dataset_phi35.jsonl
```

## Format

```json
{
  "text": "<|user|> ... <|end|><|assistant|> ... <|end|>",
  "n_tokens": 512
}
```

---

# 4. Étape 3 : Analyse de la distribution des tokens

## Script utilisé
```
scripts/analyze_tokens.py
```

## Commande
```bash
python scripts/analyze_tokens.py
```

## Ce que fait ce script

- Lit le dataset final Phi-3.5  
- Calcule :
  - moyenne des tokens  
  - maximum des tokens  
- Génère un histogramme de distribution  

## Résultat

- Vérification de compatibilité GPU  
- Détection des séquences trop longues ou trop courtes  

---

# 5. Pipeline complet (ordre d’exécution)

```bash
# 1. Nettoyage dataset brut
python scripts/prepare_data.py

# 2. Conversion Phi-3.5 + filtrage tokens
python scripts/prepare_phi35.py

# 3. Analyse qualité dataset
python scripts/analyze_tokens.py
```

---

# 6. Résultat final attendu

À la fin du pipeline :

- Dataset médical propre  
- Format compatible Phi-3.5  
- Séquences filtrées (< 4096 tokens)  
- Analyse statistique validée  
- Dataset prêt pour fine-tuning LoRA / SFT  

---

# 7. Utilisation pour entraînement (prochaine étape)

Le fichier final :

```
datasets/medical_dataset_phi35.jsonl
```

sera utilisé pour :

- LoRA fine-tuning  
- TRL SFTTrainer  
- Axolotl training pipeline  

---