
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embeddings(texts):
    
    embeddings = model.encode(texts)
    return np.array(embeddings, dtype=np.float32)

if __name__ == "__main__":
    with open("../knowledge_base/resume_tips.txt", "r", encoding="utf-8") as f:
        tips = [line.strip() for line in f.readlines() if line.strip()]

    embeddings = get_embeddings(tips)
    print(f"Created embeddings for {len(tips)} tips. Shape: {embeddings.shape}")