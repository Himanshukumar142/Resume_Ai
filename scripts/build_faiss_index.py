import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend"))

from embeddings import get_embeddings
import faiss
import numpy as np

kb_path = os.path.join(PROJECT_ROOT, "knowledge_base", "resume_tips.txt")
index_out = os.path.join(PROJECT_ROOT, "faiss_index.index")
tips_out   = os.path.join(PROJECT_ROOT, "faiss_tips.npy")

if not os.path.exists(kb_path):
    print(f"[ERROR] Knowledge base not found at: {kb_path}")
    sys.exit(1)

with open(kb_path, "r", encoding="utf-8") as f:
    tips = [line.strip() for line in f if line.strip()]

if not tips:
    print("[ERROR] resume_tips.txt is empty.")
    sys.exit(1)

print(f"[INFO] Building embeddings for {len(tips)} tips…")
embeddings = get_embeddings(tips)
dim = embeddings.shape[1]

index = faiss.IndexFlatL2(dim)
index.add(embeddings)

faiss.write_index(index, index_out)
np.save(tips_out, np.array(tips))

print(f"[OK] FAISS index saved → {index_out}")
print(f"[OK] Tips array saved  → {tips_out}")