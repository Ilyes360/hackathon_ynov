import json
import torch
from datasets import load_dataset, Dataset
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    TrainingArguments, Trainer, DataCollatorForLanguageModeling,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training

# ============================================================
# 1. Configuration
# ============================================================
BASE_MODEL = "microsoft/Phi-3.5-mini-instruct"
LOCAL_DATASET_PATH = "medical_dataset_clean.jsonl"

OUTPUT_DIR = "./medical_model_lora_experimental_v2"  # v2 pour ne pas écraser le 1er run (loss 6.52)
MAX_SAMPLES = 2000          # sous-échantillon pour rester dans le temps imparti (7h)
NUM_EPOCHS = 3
MAX_LENGTH = 512


# ============================================================
# 2. Chargement et préparation du dataset médical
# ============================================================
def load_and_clean_medical_dataset():
    import os
    suspicious_markers = ["p0up33", "poupée de cire", "poupee de cire", "j3 su1s",
                           "compliance-token", "enhanced_mode", "enhanced mode"]

    if os.path.exists(LOCAL_DATASET_PATH):
        print(f"📂 Chargement du dataset DATA (nettoyé) : {LOCAL_DATASET_PATH}")
        records = []
        skipped = 0
        with open(LOCAL_DATASET_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    skipped += 1
        if skipped:
            print(f"⚠️  {skipped} lignes ignorées (JSON invalide)")
        raw = Dataset.from_list(records)
        source = "DATA (nettoyé)"

    print(f"✅ {len(raw)} exemples bruts chargés (source : {source})")

    def is_clean(example):
        text = json.dumps(example).lower()
        return not any(marker in text for marker in suspicious_markers)

    cleaned = raw.filter(is_clean)
    removed = len(raw) - len(cleaned)
    if removed > 0:
        print(f"🚨 {removed} exemples suspects retirés (marqueurs de backdoor détectés)")
    else:
        print("✅ Aucun marqueur suspect détecté dans ce dataset")

    cleaned = cleaned.shuffle(seed=42).select(range(min(MAX_SAMPLES, len(cleaned))))
    print(f"📊 {len(cleaned)} exemples retenus pour l'entraînement")
    return cleaned


def format_for_training(example):
    # Schéma DATA : {"messages": [{"role": "user", "content": ...}, {"role": "assistant", "content": ...}]}
    if "messages" in example and example["messages"]:
        msgs = example["messages"]
        question = next((m["content"] for m in msgs if m["role"] == "user"), "")
        answer = next((m["content"] for m in msgs if m["role"] == "assistant"), "")
    else:
        # Schéma brut HuggingFace ruslanmv (Patient/Doctor), conservé en repli
        question = example.get("Patient") or example.get("question") or example.get("input", "")
        answer = example.get("Doctor") or example.get("answer") or example.get("output", "")
    text = f"<|user|>\n{question}<|end|>\n<|assistant|>\n{answer}<|end|>"
    return {"text": text}


# ============================================================
# 3. Setup modèle + LoRA
# ============================================================
def setup_model_and_tokenizer():
    print(f"🤖 Chargement du modèle de base : {BASE_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    quant_config = None
    if torch.cuda.is_available():
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )

    model_kwargs = {
        "torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32,
        "trust_remote_code": True,
        "low_cpu_mem_usage": True,
    }
    if quant_config:
        model_kwargs["quantization_config"] = quant_config
        model_kwargs["device_map"] = "auto"

    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, **model_kwargs)

    if quant_config:
        model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["qkv_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.1,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    return model, tokenizer


# ============================================================
# 4. Entraînement
# ============================================================
def train(model, tokenizer, dataset):
    def tokenize_fn(examples):
        tok = tokenizer(
            examples["text"], truncation=True, padding="max_length",
            max_length=MAX_LENGTH, return_tensors="pt",
        )
        tok["labels"] = tok["input_ids"].clone()
        return tok

    tokenized = dataset.map(tokenize_fn, batched=True, remove_columns=dataset.column_names)

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        warmup_steps=50,
        logging_steps=20,
        save_steps=200,
        save_total_limit=2,
        remove_unused_columns=False,
        dataloader_drop_last=True,
        fp16=torch.cuda.is_available(),
        report_to="none",
    )

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized,
        processing_class=tokenizer,
        data_collator=data_collator,
    )

    print("🚀 Lancement du fine-tuning LoRA (modèle EXPÉRIMENTAL)...")
    train_result = trainer.train()
    trainer.save_model()

    # Sauvegarde des métriques pour le rendu (loss, epochs)
    metrics = train_result.metrics
    with open(f"{OUTPUT_DIR}/training_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"✅ Entraînement terminé. Métriques : {metrics}")
    return trainer


# ============================================================
# 5. Test qualitatif rapide
# ============================================================
def quick_test(model, tokenizer):
    test_prompts = [
        "Quels sont les symptômes courants d'une grippe ?",
        "Quelle est la différence entre une migraine et un mal de tête classique ?",
        "Quand faut-il consulter un médecin pour de la fièvre ?",
    ]
    model.eval()
    print("\n🧪 Test qualitatif du modèle médical fine-tuné :")
    for prompt in test_prompts:
        formatted = f"<|user|>\n{prompt}<|end|>\n<|assistant|>\n"
        inputs = tokenizer(formatted, return_tensors="pt", truncation=True, max_length=MAX_LENGTH)
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model.generate(
                **inputs, max_new_tokens=150, temperature=0.7, do_sample=True,
                top_p=0.9, pad_token_id=tokenizer.eos_token_id,
            )
        response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        print(f"\n👤 {prompt}\n🤖 {response.strip()}")
        print("⚠️  Réponse à valider par un professionnel de santé — modèle expérimental, non clinique.")


# ============================================================
# Main
# ============================================================
def main():
    dataset = load_and_clean_medical_dataset()
    dataset = dataset.map(format_for_training)

    model, tokenizer = setup_model_and_tokenizer()
    train(model, tokenizer, dataset)
    quick_test(model, tokenizer)

    print("\n🎉 Pipeline de fine-tuning médical (expérimental) terminé.")
    print(f"📁 Modèle sauvegardé dans : {OUTPUT_DIR}")
    print("📌 Rappel : NE PAS déployer ce modèle en production (consigne explicite).")


if __name__ == "__main__":
    main()
