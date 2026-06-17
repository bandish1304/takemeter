"""
Fine-tune distilbert-base-uncased on the TakeMeter labeled dataset and evaluate on a held-out
test split. Produces genuine evaluation_results.json and confusion_matrix.png. Runs on CPU.
Note: this is a real local run, not the Colab T4 run, so the seed/split differ from Colab.
"""

import csv, json, random
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, precision_recall_fscore_support,
                             confusion_matrix, f1_score)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEED = 42
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)

LABELS = ["reaction", "assertion", "argument"]
L2I = {l: i for i, l in enumerate(LABELS)}
MODEL = "distilbert-base-uncased"
MAXLEN = 256
EPOCHS = 3
LR = 2e-5
BATCH = 16

# ---- load data ----
rows = list(csv.DictReader(open("labeled_dataset.csv", encoding="utf-8")))
texts = [r["text"] for r in rows]
ys = [L2I[r["label"]] for r in rows]

# stratified 70/15/15
X_tr, X_tmp, y_tr, y_tmp = train_test_split(texts, ys, test_size=0.30,
                                            stratify=ys, random_state=SEED)
X_val, X_te, y_val, y_te = train_test_split(X_tmp, y_tmp, test_size=0.50,
                                            stratify=y_tmp, random_state=SEED)
print(f"split sizes -> train {len(X_tr)}  val {len(X_val)}  test {len(X_te)}")

tok = AutoTokenizer.from_pretrained(MODEL)

class DS(Dataset):
    def __init__(self, X, y):
        self.enc = tok(X, truncation=True, padding="max_length", max_length=MAXLEN)
        self.y = y
    def __len__(self): return len(self.y)
    def __getitem__(self, i):
        item = {k: torch.tensor(v[i]) for k, v in self.enc.items()}
        item["labels"] = torch.tensor(self.y[i])
        return item

tr_dl = DataLoader(DS(X_tr, y_tr), batch_size=BATCH, shuffle=True)
val_dl = DataLoader(DS(X_val, y_val), batch_size=BATCH)
te_dl = DataLoader(DS(X_te, y_te), batch_size=BATCH)

device = torch.device("cpu")
model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=len(LABELS)).to(device)
opt = torch.optim.AdamW(model.parameters(), lr=LR)

def predict(dl):
    model.eval(); preds = []; gold = []
    with torch.no_grad():
        for b in dl:
            b = {k: v.to(device) for k, v in b.items()}
            out = model(input_ids=b["input_ids"], attention_mask=b["attention_mask"])
            preds += out.logits.argmax(-1).tolist()
            gold += b["labels"].tolist()
    return np.array(gold), np.array(preds)

for ep in range(EPOCHS):
    model.train()
    for b in tr_dl:
        b = {k: v.to(device) for k, v in b.items()}
        opt.zero_grad()
        out = model(input_ids=b["input_ids"], attention_mask=b["attention_mask"], labels=b["labels"])
        out.loss.backward(); opt.step()
    g, p = predict(val_dl)
    print(f"epoch {ep+1}: val macro-F1 = {f1_score(g, p, average='macro', zero_division=0):.3f}")

# ---- final test evaluation ----
g, p = predict(te_dl)
acc = accuracy_score(g, p)
macro = f1_score(g, p, average="macro", zero_division=0)
pr, rc, f1, sup = precision_recall_fscore_support(g, p, labels=[0,1,2], zero_division=0)
cm = confusion_matrix(g, p, labels=[0,1,2])

results = {
    "model": MODEL,
    "run": "local CPU fine-tune (not Colab T4); seed and split differ from Colab",
    "hyperparameters": {"epochs": EPOCHS, "learning_rate": LR, "batch_size": BATCH, "max_length": MAXLEN},
    "split_sizes": {"train": len(X_tr), "validation": len(X_val), "test": len(X_te)},
    "overall_accuracy": round(float(acc), 4),
    "macro_f1": round(float(macro), 4),
    "per_class": {LABELS[i]: {"precision": round(float(pr[i]), 4),
                              "recall": round(float(rc[i]), 4),
                              "f1": round(float(f1[i]), 4),
                              "support": int(sup[i])} for i in range(3)},
    "confusion_matrix": {"labels": LABELS, "rows_are_true_cols_are_pred": cm.tolist()},
}
json.dump(results, open("evaluation_results.json", "w", encoding="utf-8"), indent=2)
print(json.dumps(results, indent=2))

# dump per-example test predictions (te_dl is not shuffled, so order matches X_te)
with open("test_predictions.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["text", "true", "pred", "correct"])
    for t, gt, pp in zip(X_te, g, p):
        w.writerow([t, LABELS[gt], LABELS[pp], int(gt == pp)])
model.save_pretrained("finetuned_model"); tok.save_pretrained("finetuned_model")
print("saved test_predictions.csv and finetuned_model/")

# ---- confusion matrix image ----
fig, ax = plt.subplots(figsize=(5, 4.2))
im = ax.imshow(cm, cmap="Blues")
ax.set_xticks(range(3)); ax.set_yticks(range(3))
ax.set_xticklabels(LABELS); ax.set_yticklabels(LABELS)
ax.set_xlabel("Predicted"); ax.set_ylabel("True")
ax.set_title("Fine-tuned DistilBERT — test confusion matrix")
for i in range(3):
    for j in range(3):
        ax.text(j, i, cm[i, j], ha="center", va="center",
                color="white" if cm[i, j] > cm.max()/2 else "black")
fig.colorbar(im); fig.tight_layout()
fig.savefig("confusion_matrix.png", dpi=130)
print("wrote evaluation_results.json and confusion_matrix.png")
