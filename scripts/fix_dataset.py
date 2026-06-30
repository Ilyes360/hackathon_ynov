import json

input_file = 'datasets/test_dataset_16000.json'
output_file = 'medical_dataset_final_fixed.jsonl'

print("Nettoyage profond en cours...")

with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for i, line in enumerate(infile):
            try:
                # On tente de parser la ligne
                data = json.loads(line)
                # On réécrit proprement
                outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
            except:
                # Si la ligne est vraiment cassée, on l'ignore silencieusement
                continue

print(f"Fichier corrigé généré : {output_file}")