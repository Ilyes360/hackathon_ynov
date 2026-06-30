import matplotlib.pyplot as plt
import json

lengths = []

with open("datasets/medical_dataset_phi35.jsonl") as f:
    for line in f:
        lengths.append(json.loads(line)["n_tokens"])

print("Moyenne tokens:", sum(lengths)/len(lengths))
print("Max tokens:", max(lengths))

plt.hist(lengths, bins=50)
plt.title("Distribution tokens - dataset médical Phi-3.5")
plt.show()