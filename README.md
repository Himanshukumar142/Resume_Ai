# 📄 Resume ATS Scorer

> **An intelligent, full-stack web application that analyzes your resume against any job description and gives you an ATS (Applicant Tracking System) compatibility score — powered by NLP, FAISS vector search, and Google Gemini AI.**

<br>

---

## 🌟 Features at a Glance

| Feature | Description |
|---|---|
| ⚡ **Instant ATS Score** | Upload your resume and get a score out of 100 in seconds — no login required |
| 🔑 **Full Dashboard** | Authenticated users get a detailed breakdown with matched/missing keywords and AI suggestions |
| 🤖 **Gemini AI Coach** | Google Gemini 2.5 Flash generates 5 personalized, actionable improvement suggestions |
| 🔍 **FAISS RAG Pipeline** | Retrieves the most relevant resume tips from a curated knowledge base using semantic search |
| 🛡️ **Secure Auth** | Flask-Login + Werkzeug password hashing + CSRF protection on all forms |
| 📊 **Multi-Component Scoring** | 4-factor scoring: Keyword Match, Cosine Similarity, Section Structure, and Achievements |
| 📁 **PDF & DOCX Support** | Upload resumes in PDF or DOCX format — text is extracted and then the file is discarded |

<br>

---

## 🏗️ Project Structure

```
pyhton_resume/
│
├── 📂 backend/                  # Flask application (Python)
│   ├── app.py                   # 🚀 App entry point — Flask factory, blueprints, CSRF
│   ├── routes.py                # 🌐 API routes (/ats_score, /process_resume)
│   ├── auth.py                  # 🔐 Auth blueprint (register, login, logout)
│   ├── models.py                # 🗄️ User model — SQLite via raw SQL + Flask-Login
│   ├── scoring.py               # 🧠 Core ATS scoring engine (no ML dependencies)
│   ├── rag.py                   # 🤖 RAG pipeline — FAISS retrieval + Gemini AI
│   ├── resume_parser.py         # 📄 PDF/DOCX text extraction
│   ├── embeddings.py            # 🔢 Sentence embedding helpers
│   ├── config.py                # ⚙️ App configuration & file validation
│   ├── requirements.txt         # 📦 Python dependencies
│   ├── .env                     # 🔒 Environment variables (SECRET_KEY, GEMINI_API_KEY)
│   ├── users.db                 # 🗃️ SQLite user database (auto-created)
│   │
│   ├── 📂 templates/            # Jinja2 HTML templates
│   │   ├── landing.html         # 🏠 Public landing page with free ATS checker
│   │   ├── index.html           # 📊 Full dashboard (login required)
│   │   ├── login.html           # 🔑 Login page
│   │   └── register.html        # 📝 Registration page
│   │
│   └── 📂 static/               # Backend static assets (CSS, JS)
│
├── 📂 frontend/                 # Standalone frontend assets
│   ├── index.html               # Frontend entry point
│   ├── dashboard.html           # Dashboard UI
│   └── 📂 static/               # JS and CSS files
│
├── 📂 scripts/                  # Utility scripts
│   ├── build_faiss_index.py     # 🏗️ Builds/rebuilds the FAISS vector index
│   ├── download_resume.py       # ⬇️ Downloads sample resumes for testing
│   └── test_rag.py              # 🧪 Tests the RAG pipeline end-to-end
│
├── 📂 knowledge_base/           # Raw resume tips used to build the FAISS index
├── 📂 database/                 # Additional data files
├── faiss_index.index            # 🗂️ Serialized FAISS vector index
├── faiss_tips.npy               # 💾 NumPy array of tip strings (paired with index)
└── .gitignore                   # Git exclusion rules
```

<br>

---

## 🧠 How the ATS Scoring Works

The scoring engine in `scoring.py` is built **entirely from scratch** — no heavy ML models required for the score itself. It uses **four weighted components**:

```
Final Score = (Keyword Match × 40%) + (Cosine Similarity × 25%) + (Section Structure × 20%) + (Achievements × 15%)
```

| Component | Weight | What It Measures |
|---|---|---|
| 🔤 **Keyword Match** | 40% | Weighted overlap of technical skills, tools, and soft skills between your resume and the JD |
| 📐 **Cosine Similarity** | 25% | TF-based cosine similarity of overall vocabulary between resume and JD |
| 📋 **Section Structure** | 20% | Presence of key sections: Summary, Skills, Experience, Projects, Education, Certifications |
| 🏆 **Achievements** | 15% | Quantifiable results (percentages, dollar values, multipliers) and strong action verbs |

### 🔑 Keyword Categories & Weights

| Category | Weight | Examples |
|---|---|---|
| ⚙️ Technical Skills | `3.0×` | Python, React, Docker, TensorFlow, AWS, PostgreSQL |
| 🛠️ Tools & Frameworks | `2.0×` | Jira, Tableau, GitHub, VS Code, Salesforce |
| 🤝 Soft Skills | `1.0×` | Leadership, Communication, Agile, Problem Solving |

> 💡 Keywords that appear multiple times in your resume receive a small frequency bonus (up to **1.5×**), rewarding naturally integrated skills over keyword stuffing.

<br>

---

## 🤖 RAG + Gemini AI Pipeline

For **logged-in users**, the `/process_resume` endpoint runs the full AI pipeline:

```
1. 🧮 Run full ATS analysis  →  score + matched/missing keywords
2. 🔍 Query FAISS index      →  retrieve top-3 semantically relevant resume tips
3. 📝 Build Gemini prompt    →  resume text + JD + keyword gaps + retrieved tips
4. ✨ Call Gemini 2.5 Flash  →  5 structured, actionable improvement suggestions
```

The FAISS index is built using `sentence-transformers` (`all-MiniLM-L6-v2`) over the curated tips in `knowledge_base/`. To rebuild the index:

```bash
python scripts/build_faiss_index.py
```

<br>

---

## 🔐 Authentication & Security

| Mechanism | Implementation |
|---|---|
| 🔒 Password Hashing | `werkzeug.security.generate_password_hash` (PBKDF2-HMAC-SHA256) |
| 🍪 Session Management | `flask-login` with secure, HttpOnly session cookies |
| 🛡️ CSRF Protection | `flask-wtf.csrf.CSRFProtect` applied globally to all POST forms |
| 🗄️ Database | SQLite (`users.db`) with parameterized queries — no SQL injection risk |
| 🔑 Secret Key | Loaded from `backend/.env` — never hardcoded |

**Route protection summary:**

- `GET /` → Public landing page with free ATS score checker
- `POST /ats_score` → Public — returns numeric score only
- `GET /dashboard` → 🔒 Login required
- `POST /process_resume` → 🔒 Login required — full AI analysis

<br>

---

## 🚀 Getting Started

### ✅ Prerequisites

- Python **3.9+**
- `pip`
- A **Google Gemini API key** (free tier available at [Google AI Studio](https://aistudio.google.com/))

<br>

### 📦 Installation

**1. Clone the repository**

```bash
git clone https://github.com/your-username/pyhton_resume.git
cd pyhton_resume
```

**2. Create and activate a virtual environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r backend/requirements.txt
```

**4. Configure environment variables**

Create (or edit) `backend/.env`:

```env
SECRET_KEY=your-super-secret-key-change-this
GEMINI_API_KEY=your-gemini-api-key-here
```

> ⚠️ **Never commit `.env` to version control.** It is already included in `.gitignore`.

**5. (Optional) Rebuild the FAISS index**

```bash
python scripts/build_faiss_index.py
```

> The pre-built `faiss_index.index` and `faiss_tips.npy` are already included in the repository.

<br>

### ▶️ Running the Application

```bash
cd backend
python app.py
```

Open your browser and navigate to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

<br>

---

## 🌐 API Reference

### `POST /ats_score` — Public ATS Score

Get a quick numeric ATS compatibility score. No authentication required.

**Request** (`multipart/form-data`):

| Field | Type | Required | Description |
|---|---|---|---|
| `resume` | File | ✅ | PDF or DOCX resume file |
| `job_description` | String | ✅ | Full job description text |

**Response** (`200 OK`):

```json
{
  "score": 74.5
}
```

**Error Responses:**

| Status | Condition |
|---|---|
| `400` | Missing resume file or job description |
| `400` | Unsupported file type (not PDF/DOCX) |
| `422` | Text could not be extracted from file |
| `500` | Internal server dependency error |

---

### `POST /process_resume` — Full AI Analysis 🔒

Get the complete analysis including keyword breakdown, FAISS-retrieved tips, and Gemini AI suggestions. **Requires login.**

**Request** (`multipart/form-data`):

| Field | Type | Required | Description |
|---|---|---|---|
| `resume` | File | ✅ | PDF or DOCX resume file |
| `job_description` | String | ✅ | Full job description text |

**Response** (`200 OK`):

```json
{
  "score": 74.5,
  "retrieved_tips": [
    "Tip 1 from knowledge base...",
    "Tip 2 from knowledge base...",
    "Tip 3 from knowledge base..."
  ],
  "ai_suggestions": "1. Add Missing Keywords\n   Problem: ...\n   Solution: ..."
}
```

---

### `GET/POST /auth/register` — Register

Register a new user account.

### `GET/POST /auth/login` — Login

Log in with email and password.

### `GET /auth/logout` — Logout 🔒

Log out the currently authenticated user.

<br>

---

## 📦 Dependencies

```
flask>=2.3.0              # Web framework
python-dotenv>=1.0.0      # Environment variable loading
pdfminer.six>=20221105    # PDF text extraction
python-docx>=0.8.11       # DOCX text extraction
sentence-transformers>=2.2.2  # Semantic embeddings for FAISS
faiss-cpu>=1.7.4          # Vector similarity search
numpy>=1.24.0             # Numerical arrays
google-generativeai>=0.7.0    # Gemini AI API
flask-login>=0.6.3        # User session management
werkzeug>=2.3.0           # Password hashing + WSGI utilities
```

<br>

---

## 🗂️ File Upload Policy

- ✅ Accepted formats: **PDF** and **DOCX** only
- 📏 Maximum file size: **10 MB**
- 🔐 Files are saved temporarily, text is extracted, and then the **file is immediately deleted** from the server — your resume is never stored persistently

<br>

---

## 🧪 Testing

**Test the RAG pipeline end-to-end:**

```bash
python scripts/test_rag.py
```

**Run the scoring engine standalone:**

```bash
python backend/scoring.py
```
> This runs the built-in `__main__` block with a sample resume and job description, printing a full ATS report to the console.

<br>

---

## 📁 Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Flask session signing key — use a long random string in production |
| `GEMINI_API_KEY` | ⚠️ Optional | Google Gemini API key — AI suggestions are disabled if not set |

<br>

---

## 🗺️ Roadmap

- [ ] 📈 Store and display historical ATS score trends per user
- [ ] 🌍 Multi-language resume support
- [ ] 📧 Email verification on registration
- [ ] 📤 Resume export with AI-applied suggestions
- [ ] 🔗 LinkedIn job posting URL parser (auto-fill JD)
- [ ] 🌙 Dark / light mode toggle on dashboard

<br>

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. 🍴 Fork the repository
2. 🌿 Create a feature branch: `git checkout -b feature/your-feature-name`
3. 💾 Commit your changes: `git commit -m "feat: add your feature"`
4. 📤 Push to the branch: `git push origin feature/your-feature-name`
5. 🔁 Open a Pull Request

<br>

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

<br>

---

## 👤 Author

Made with ❤️ and a lot of ☕ by **hroya**

> ⭐ If this project helped you, consider giving it a star on GitHub!