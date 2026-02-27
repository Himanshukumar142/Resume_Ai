# rag.py
import os
import faiss
import numpy as np
from embeddings import get_embeddings
from sentence_transformers import SentenceTransformer
from scoring import compute_score
import google.generativeai as genai

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
faiss_index_path = os.path.join(project_root, "faiss_index.index")
tips_path = os.path.join(project_root, "faiss_tips.npy")

faiss_index = None
tips = []
try:
    if os.path.exists(faiss_index_path):
        faiss_index = faiss.read_index(faiss_index_path)
    else:
        print(f"[WARNING] FAISS index not found at {faiss_index_path}")
    if os.path.exists(tips_path):
        tips = np.load(tips_path, allow_pickle=True).tolist()
    else:
        print(f"[WARNING] Tips file not found at {tips_path}")
except Exception as e:
    print(f"[ERROR] Could not load FAISS index or tips: {e}")
    faiss_index = None
    tips = []

model = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_tips(resume_text: str, job_description: str, top_k: int = 3) -> list:
    """Retrieve top-k relevant tips from FAISS index."""
    query_text = resume_text + " " + job_description

    if faiss_index is None or not tips:
        return tips[:top_k]

    try:
        query_vec = model.encode([query_text]).astype(np.float32)
        distances, indices = faiss_index.search(query_vec, top_k)
        retrieved = [tips[i] for i in indices[0] if i < len(tips)]
        return retrieved
    except Exception as e:
        print(f"[ERROR] FAISS search failed: {e}")
        return tips[:top_k]


def get_suggestions(resume_text: str, job_description: str, top_k: int = 3) -> dict:
    """
    Full RAG pipeline:
        1. Compute ATS score + extract keyword gaps (new rule-based engine)
        2. Retrieve top-k tips from FAISS
        3. Send context + keyword gaps to Gemini for actionable suggestions
    """
    try:
        try:
            from backend.scoring import full_ats_analysis
        except Exception:
            from scoring import full_ats_analysis
    except Exception:
        from scoring import compute_score
        score = compute_score(resume_text, job_description)
        full_result = {"score": score, "matched_keywords": [], "missing_keywords": [], "suggestions": []}
    else:
        full_result = full_ats_analysis(resume_text, job_description)

    score = full_result["score"]

    matched_kws = ", ".join(k for k, _ in full_result.get("matched_keywords", [])[:10]) or "None detected"
    missing_kws = ", ".join(k for k, _ in full_result.get("missing_keywords", [])[:10]) or "None detected"

    retrieved_tips = retrieve_tips(resume_text, job_description, top_k)

    tips_text = "\n- ".join(retrieved_tips) if retrieved_tips else "No specific tips available."
    prompt = f"""You are a professional resume coach. Analyze the resume against the job description and provide exactly 5 actionable suggestions to improve the resume's match.

Resume:
{resume_text[:3000]}

Job Description:
{job_description[:2000]}

ATS Keyword Analysis:
- Keywords MATCHED in resume: {matched_kws}
- Keywords MISSING from resume: {missing_kws}

Relevant Resume Tips:
- {tips_text}

STRICT OUTPUT FORMAT — follow this exactly for each suggestion. Do NOT use any markdown symbols like **, *, #, or _.

1. [Short Title of Suggestion]
   Problem: Describe the specific gap or issue found in the resume relative to the job description.
   Solution: Provide a clear, actionable fix with specific details from the resume and job description.

2. [Short Title of Suggestion]
   Problem: ...
   Solution: ...

(continue for suggestions 3, 4, and 5)

Rules:
- Use plain text only. No asterisks, no bold, no bullet dashes inside sub-points.
- Each suggestion must have a numbered title, a Problem line, and a Solution line.
- Prioritize missing keywords from the ATS Analysis above — address those gaps specifically.
- Be specific — reference actual skills, tools, or sections from the resume and job description."""

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[WARNING] GEMINI_API_KEY not set; skipping LLM call")
        ai_suggestions = (
            "AI suggestions are disabled — set GEMINI_API_KEY in backend/.env to enable them."
        )
    else:
        try:
            genai.configure(api_key=api_key)
            gemini_model = genai.GenerativeModel(model_name="gemini-2.5-flash")
            response = gemini_model.generate_content(prompt)
            ai_suggestions = response.text
        except Exception as e:
            err_msg = str(e).lower()
            if "api_key" in err_msg or "credential" in err_msg or "authentication" in err_msg:
                print("[ERROR] Gemini authentication failed — check GEMINI_API_KEY")
                ai_suggestions = "Authentication failed. Please check your Gemini API key in backend/.env"
            elif "quota" in err_msg or "rate" in err_msg or "429" in err_msg:
                print("[ERROR] Gemini rate limit exceeded")
                ai_suggestions = "Gemini rate limit exceeded. Please try again shortly."
            else:
                print(f"[ERROR] Gemini API call failed: {e}")
                ai_suggestions = f"Could not generate AI suggestions: {e}"

    return {
        "score": float(score),
        "retrieved_tips": retrieved_tips,
        "ai_suggestions": ai_suggestions,
    }