from transformers import AutoTokenizer
import json

model_id = "microsoft/Phi-3.5-mini-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)

MAX_SEQ_LENGTH = 4096

input_file = "datasets/medical_dataset_clean.jsonl"
output_file = "datasets/medical_dataset_phi35.jsonl"

def count_tokens(text):
    return len(tokenizer.encode(text))

filtered = []

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        sample = json.loads(line)
        messages = sample["messages"]

        # 🔥 conversion Phi-3.5 OFFICIELLE
        formatted = tokenizer.apply_chat_template(
            messages,
            tokenize=False
        )

        token_len = count_tokens(formatted)

        # FILTER
        if token_len <= MAX_SEQ_LENGTH:
            filtered.append({
                "text": formatted,
                "n_tokens": token_len
            })

with open(output_file, "w", encoding="utf-8") as f:
    for item in filtered:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"OK - {len(filtered)} samples validés")