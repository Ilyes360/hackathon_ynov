import pandas as pd
from datasets import load_dataset
import json

print("1. Téléchargement du dataset médical depuis Hugging Face...")
# Charge le dataset ciblé par l'énoncé
dataset = load_dataset("ruslanmv/ai-medical-chatbot", split="train")
df = dataset.to_pandas()

print(f"Volume initial : {len(df)} conversations")

print("2. Nettoyage intensif (Mode Hackathon)...")
# Suppression des valeurs nulles
df_clean = df.dropna(subset=['Patient', 'Doctor'])

# Suppression des doublons stricts pour éviter l'overfitting
df_clean = df_clean.drop_duplicates(subset=['Patient'])

# Filtrage de qualité des conversations (< 50 caractères)
df_clean = df_clean[df_clean['Doctor'].str.len() > 50]

print(f"Volume après nettoyage : {len(df_clean)} conversations qualifiées")

print("3. Formatage pour l'entraînement LoRA (Format ChatML)...")
formatted_data = []
for index, row in df_clean.iterrows():
    # Structure ChatML attendue par la majorité des scripts de fine-tuning modernes
    chat = {
        "messages": [
            {"role": "user", "content": str(row['Patient']).strip()},
            {"role": "assistant", "content": str(row['Doctor']).strip()}
        ]
    }
    formatted_data.append(chat)

print("4. Exportation du dataset final...")
output_file = "medical_dataset_clean.jsonl"
with open(output_file, 'w', encoding='utf-8') as f:
    for item in formatted_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f"Mission accomplie ! Fichier '{output_file}' généré.")