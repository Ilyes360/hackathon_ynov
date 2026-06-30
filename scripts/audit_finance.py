import pandas as pd
import json

# Charger le dataset financier
with open('datasets/finance_dataset_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Audit rapide
print(f"--- Rapport Qualité Finance ---")
print(f"Nombre total d'entrées : {len(df)}")
print(f"Colonnes présentes : {df.columns.tolist()}")

# Vérifier s'il y a des valeurs manquantes dans les colonnes critiques (ex: 'instruction' ou 'output')
missing = df.isnull().sum()
print(f"\nValeurs manquantes par colonne :\n{missing}")

# Vérifier la longueur moyenne des réponses pour voir si elles sont assez détaillées
if 'output' in df.columns:
    avg_len = df['output'].str.len().mean()
    print(f"\nLongueur moyenne des réponses financières : {avg_len:.0f} caractères")