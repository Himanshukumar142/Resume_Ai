import re
import math
import string
from collections import Counter

STOPWORDS = {
    "a","about","above","after","again","against","all","am","an","and","any",
    "are","as","at","be","because","been","before","being","below","between",
    "both","but","by","can","did","do","does","doing","down","during","each",
    "few","for","from","further","get","got","had","has","have","having","he",
    "her","here","him","his","how","i","if","in","into","is","it","its","just",
    "me","more","most","my","no","nor","not","now","of","off","on","once",
    "only","or","other","our","out","over","own","s","same","she","should",
    "so","some","such","t","than","that","the","their","them","then","there",
    "these","they","this","those","through","to","too","under","until","up",
    "us","very","was","we","were","what","when","where","which","while","who",
    "whom","why","will","with","you","your","also","may","must","would","could",
    "shall","need","per","via","new","use","using","used","work","working",
    "able","well","good","great","strong","help","please","come","make","build",
    "join","team","role","part","looking","seeking","requires","required",
    "minimum","least","least","experience","years","year","day","days","time",
    "based","across","within","throughout","multiple","various","including",
    "including","ensure","ensuring","support","lead","leading","manage","will",
    "provide","develop","design","maintain","implement","responsible",
    "opportunity","position","successful","candidate","ability","preferred",
    "plus","bonus","ideally","nice","equivalent","related","relevant",
}

TECHNICAL_SKILLS = {
    
    "python","java","javascript","typescript","c","c++","c#","ruby","go","rust",
    "kotlin","swift","scala","r","matlab","perl","php","bash","shell","sql",
    "html","css","sass","graphql","solidity","dart","lua","haskell","elixir",
    
    "machine learning","deep learning","nlp","natural language processing",
    "computer vision","tensorflow","pytorch","keras","scikit","pandas","numpy",
    "matplotlib","seaborn","data science","data analysis","statistics",
    "regression","classification","clustering","neural network","lstm","bert",
    "transformers","hugging face","xgboost","lightgbm","random forest",
    
    "aws","azure","gcp","google cloud","docker","kubernetes","terraform",
    "ansible","jenkins","ci/cd","devops","linux","unix","git","github",
    "gitlab","bitbucket","nginx","apache","hadoop","spark","kafka","airflow",
    
    "mysql","postgresql","postgres","mongodb","redis","sqlite","oracle",
    "dynamodb","cassandra","elasticsearch","neo4j","firebase","supabase",
    "bigquery","snowflake","databricks",
    
    "react","angular","vue","nextjs","nuxtjs","node","nodejs","express",
    "django","flask","fastapi","spring","springboot","rails","laravel","dotnet",
    "asp.net","jquery","redux","graphql","rest","api","restful",
    
    "cybersecurity","penetration testing","owasp","encryption","oauth",
    "ssl","tls","firewall","vpn","siem","soc","threat","vulnerability",
    
    "agile","scrum","kanban","jira","confluence","microservices","serverless",
    "blockchain","iot","embedded","arduino","raspberry","fpga","verilog",
    "solidworks","autocad","figma","sketch","adobe","photoshop",
}

TOOLS_FRAMEWORKS = {
    "excel","powerpoint","word","tableau","powerbi","looker","dbt","sas",
    "spss","jira","trello","notion","slack","github","gitlab","bitbucket",
    "vs code","visual studio","pycharm","intellij","eclipse","postman",
    "swagger","insomnia","circleci","travis","heroku","netlify","vercel",
    "shopify","wordpress","magento","salesforce","hubspot","sap","servicenow",
    "zendesk",
}

SOFT_SKILLS = {
    "communication","leadership","teamwork","collaboration","problem solving",
    "critical thinking","creativity","adaptability","time management",
    "attention to detail","project management","analytical","organized",
    "interpersonal","presentation","mentoring","coaching","decision making",
    "fast learner","self motivated","proactive","flexible","multitasking",
    "conflict resolution","stakeholder management","customer service",
}

SECTION_PATTERNS = {
    "skills":       r"\b(skills|technical skills|core competencies|technologies|competencies)\b",
    "experience":   r"\b(experience|work experience|employment|professional experience|career)\b",
    "projects":     r"\b(projects|personal projects|key projects|portfolio|case studies)\b",
    "education":    r"\b(education|academic|qualifications|degree|university|college)\b",
    "certifications": r"\b(certifications?|certificates?|credential|licensed)\b",
    "summary":      r"\b(summary|objective|profile|about me|overview)\b",
}
ACTION_VERBS = {
    "achieved","improved","reduced","increased","developed","designed","built",
    "created","launched","delivered","led","managed","automated","optimized",
    "deployed","migrated","integrated","scaled","saved","generated","grew",
    "accelerated","restructured","transformed","established","spearheaded",
    "implemented","architected","engineered","streamlined","negotiated",
    "coordinated","mentored","trained","published","contributed","resolved",
}

def _clean(text: str) -> str:
    """Lowercase + remove punctuation (keep spaces)."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text) 
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _stem(word: str) -> str:
    """
    Minimal suffix-stripping stemmer (no ML).
    Handles common English inflections.
    """
    if len(word) <= 3:
        return word
    
    suffixes = [
        "ational","tional","enci","anci","izer","ising","izing",
        "alism","ness","ment","ists","ings","ated","ates","ator",
        "alism","ness","ful","ous","ive","ize","ise","ate","ical",
        "ness","less","ment","able","ible","sion","tion",
        "ing","ed","er","es","ly","al","en","ic","ry",
    ]
    for suffix in suffixes:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: len(word) - len(suffix)]
    
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("ves") and len(word) > 4:
        return word[:-3] + "f"
    if word.endswith("ses") or word.endswith("xes") or word.endswith("zes"):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word


def _tokenize(text: str, stem: bool = True) -> list:
    """Clean → tokenize → remove stopwords → optional stem."""
    cleaned = _clean(text)
    tokens  = cleaned.split()
    tokens  = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
    if stem:
        tokens = [_stem(t) for t in tokens]
    return tokens


def _bigrams(tokens: list) -> list:
    """Generate word bigrams for two-word phrase matching."""
    return [tokens[i] + " " + tokens[i + 1] for i in range(len(tokens) - 1)]

WEIGHTS = {"technical": 3.0, "tool": 2.0, "soft": 1.0}
MAX_FREQ_BONUS = 1.5 


def _extract_weighted_keywords(text: str) -> dict:
    """
    Scan text for known skill keywords and assign category + weight.
    Returns {keyword: (category, weight)}.
    Also extracts unigrams not in the dictionaries (generic technical terms).
    """
    text_lower = text.lower()
    found = {}

    for phrase in sorted(TECHNICAL_SKILLS, key=len, reverse=True):
        if len(phrase.split()) > 1 and phrase in text_lower:
            found[phrase] = ("technical", WEIGHTS["technical"])
    for phrase in sorted(TOOLS_FRAMEWORKS, key=len, reverse=True):
        if len(phrase.split()) > 1 and phrase in text_lower:
            found[phrase] = ("tool", WEIGHTS["tool"])
    for phrase in sorted(SOFT_SKILLS, key=len, reverse=True):
        if len(phrase.split()) > 1 and phrase in text_lower:
            found[phrase] = ("soft", WEIGHTS["soft"])

    tokens_raw = _tokenize(text, stem=False)
    tokens_stem = [_stem(t) for t in tokens_raw]

    for kw in TECHNICAL_SKILLS:
        if len(kw.split()) == 1:
            kw_stem = _stem(kw)
            if kw_stem in tokens_stem and kw not in found:
                found[kw] = ("technical", WEIGHTS["technical"])
    for kw in TOOLS_FRAMEWORKS:
        if len(kw.split()) == 1:
            kw_stem = _stem(kw)
            if kw_stem in tokens_stem and kw not in found:
                found[kw] = ("tool", WEIGHTS["tool"])
    for kw in SOFT_SKILLS:
        if len(kw.split()) == 1:
            kw_stem = _stem(kw)
            if kw_stem in tokens_stem and kw not in found:
                found[kw] = ("soft", WEIGHTS["soft"])

    return found


def _keyword_score(resume_text: str, jd_text: str):
    """
    Returns:
        score          0-100 keyword match score
        matched_kws    list of matched keywords with category
        missing_kws    list of JD keywords absent from resume
    """
    jd_kws     = _extract_weighted_keywords(jd_text)
    resume_kws = _extract_weighted_keywords(resume_text)

    if not jd_kws:
        return 0.0, [], []

    resume_lower = resume_text.lower()

    weighted_total  = 0.0
    weighted_match  = 0.0
    matched_list    = []
    missing_list    = []

    for kw, (cat, weight) in jd_kws.items():
        weighted_total += weight
        if kw in resume_kws:
            
            freq  = resume_lower.count(kw)
            bonus = min(1.0 + 0.1 * (freq - 1), MAX_FREQ_BONUS)
            weighted_match += weight * bonus
            matched_list.append((kw, cat))
        else:
            missing_list.append((kw, cat))

    if weighted_total == 0:
        return 0.0, matched_list, missing_list

    raw = (weighted_match / weighted_total) * 100
    
    score = raw * (1 - 0.15 * (raw / 100))
    return min(score, 100.0), matched_list, missing_list


def _tf(tokens: list) -> dict:
    """Term frequency: count / total."""
    total  = len(tokens) or 1
    counts = Counter(tokens)
    return {t: c / total for t, c in counts.items()}


def _cosine_similarity(vec_a: dict, vec_b: dict) -> float:
    """Cosine similarity between two TF dicts."""
    vocab   = set(vec_a) | set(vec_b)
    dot     = sum(vec_a.get(t, 0) * vec_b.get(t, 0) for t in vocab)
    mag_a   = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    mag_b   = math.sqrt(sum(v ** 2 for v in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def _cosine_score(resume_text: str, jd_text: str) -> float:
    """TF-based cosine similarity score 0-100."""
    r_tokens = _tokenize(resume_text)
    j_tokens = _tokenize(jd_text)
    if not r_tokens or not j_tokens:
        return 0.0
    sim = _cosine_similarity(_tf(r_tokens), _tf(j_tokens))
    return sim * 100


SECTION_WEIGHTS = {
    "skills":         15,
    "experience":     20,
    "projects":       10,
    "education":      10,
    "certifications": 5,
    "summary":        5,
}
SECTION_MAX = sum(SECTION_WEIGHTS.values()) 


def _section_score(resume_text: str) -> tuple:
    """Returns (score_0_to_100, dict of found sections)."""
    text  = resume_text.lower()
    found = {}
    total = 0
    for sec, pattern in SECTION_PATTERNS.items():
        if re.search(pattern, text):
            found[sec] = True
            total += SECTION_WEIGHTS.get(sec, 5)
    score = (total / SECTION_MAX) * 100
    return score, found

def _achievement_score(resume_text: str) -> float:
    """
    Detects:
    - Measurable results (numbers with %, $, x, or words like 'million')
    - Strong action verbs
    Returns score 0-100
    """
    text      = resume_text.lower()
    tokens    = text.split()

    metric_pattern = re.compile(
        r"""
        (\d+\.?\d*\s*%)           |  
        (\$\s*\d[\d,]*\.?\d*)    |  
        (\d+\.?\d*\s*x\b)        |  
        (\d[\d,]+\s*(million|billion|k\b|thousand))  |  
        (reduced|increased|improved).*?\d+           
        """,
        re.IGNORECASE | re.VERBOSE,
    )
    metric_hits = len(metric_pattern.findall(resume_text))

    verb_hits = sum(1 for t in tokens if t in ACTION_VERBS)

    metric_score = min(metric_hits / 5, 1.0) * 50
    verb_score   = min(verb_hits   / 8, 1.0) * 50

    return metric_score + verb_score 


def _generate_suggestions(
    missing_kws: list,
    found_sections: dict,
    achievement_score: float,
    cosine: float,
) -> list:
    """Return up to 6 actionable, rule-based improvement suggestions."""
    suggestions = []

    tech_missing  = [k for k, c in missing_kws if c == "technical"]
    tool_missing  = [k for k, c in missing_kws if c == "tool"]
    soft_missing  = [k for k, c in missing_kws if c == "soft"]

    if tech_missing:
        kws = ", ".join(tech_missing[:5])
        suggestions.append(
            f"Add missing technical skills to your Skills section: {kws}."
        )
    if tool_missing:
        kws = ", ".join(tool_missing[:4])
        suggestions.append(
            f"Mention these tools/technologies from the job description: {kws}."
        )

    if "summary" not in found_sections:
        suggestions.append(
            "Add a professional Summary/Objective section at the top of your resume."
        )
    if "skills" not in found_sections:
        suggestions.append(
            "Add a dedicated Skills section listing your technical and soft skills."
        )
    if "projects" not in found_sections:
        suggestions.append(
            "Include a Projects section to demonstrate hands-on experience."
        )
    if "certifications" not in found_sections and len(suggestions) < 5:
        suggestions.append(
            "Consider adding a Certifications section for relevant credentials."
        )

    if achievement_score < 40:
        suggestions.append(
            "Quantify achievements in your Experience section (e.g., 'Reduced load time by 30%', "
            "'Led a team of 5 engineers'). Use strong action verbs."
        )

    if cosine < 35:
        suggestions.append(
            "Your resume content is quite different from the job description. "
            "Mirror the language used in the JD more closely in your Experience bullet points."
        )

    if soft_missing and len(suggestions) < 6:
        kws = ", ".join(soft_missing[:3])
        suggestions.append(
            f"Highlight soft skills expected for this role: {kws}."
        )

    return suggestions[:6]


def compute_score(resume_text: str, job_description_text: str) -> float:
    """
    Backward-compatible entry point.  Returns a single float 0-100.
    Kept for callers that only need the numeric score (e.g. /ats_score route).
    """
    return full_ats_analysis(resume_text, job_description_text)["score"]


def full_ats_analysis(resume_text: str, job_description_text: str) -> dict:
    """
    Full ATS analysis. Returns:
    {
        "score":              float (0-100),
        "keyword_score":      float,
        "cosine_score":       float,
        "section_score":      float,
        "achievement_score":  float,
        "matched_keywords":   [(kw, category), ...],
        "missing_keywords":   [(kw, category), ...],
        "found_sections":     {section: True, ...},
        "suggestions":        [str, ...],
        "breakdown":          {component: contribution, ...},
    }
    """
    if not resume_text or not job_description_text:
        return _empty_result()

    kw_score, matched, missing  = _keyword_score(resume_text, job_description_text)
    cos_score                   = _cosine_score(resume_text, job_description_text)
    sec_score, found_sections   = _section_score(resume_text)
    ach_score                   = _achievement_score(resume_text)

    WEIGHTS_FINAL = {
        "keyword":     0.40,
        "cosine":      0.25,
        "section":     0.20,
        "achievement": 0.15,
    }

    raw_score = (
        kw_score  * WEIGHTS_FINAL["keyword"]  +
        cos_score * WEIGHTS_FINAL["cosine"]   +
        sec_score * WEIGHTS_FINAL["section"]  +
        ach_score * WEIGHTS_FINAL["achievement"]
    )

    if raw_score > 60:
        excess  = raw_score - 60
        adjusted = 60 + excess * 0.75
    else:
        adjusted = raw_score

    final_score = round(min(adjusted, 92.0), 1)

    suggestions = _generate_suggestions(missing, found_sections, ach_score, cos_score)

    breakdown = {
        "Keyword Match (40%)":    round(kw_score  * WEIGHTS_FINAL["keyword"],  1),
        "Cosine Similarity (25%)": round(cos_score * WEIGHTS_FINAL["cosine"],  1),
        "Section Structure (20%)": round(sec_score * WEIGHTS_FINAL["section"], 1),
        "Achievements (15%)":      round(ach_score * WEIGHTS_FINAL["achievement"], 1),
    }

    return {
        "score":             final_score,
        "keyword_score":     round(kw_score,  1),
        "cosine_score":      round(cos_score, 1),
        "section_score":     round(sec_score, 1),
        "achievement_score": round(ach_score, 1),
        "matched_keywords":  matched,
        "missing_keywords":  missing,
        "found_sections":    found_sections,
        "suggestions":       suggestions,
        "breakdown":         breakdown,
    }


def _empty_result() -> dict:
    return {
        "score": 0.0,
        "keyword_score": 0.0,
        "cosine_score": 0.0,
        "section_score": 0.0,
        "achievement_score": 0.0,
        "matched_keywords": [],
        "missing_keywords": [],
        "found_sections": {},
        "suggestions": ["Please provide valid resume and job description text."],
        "breakdown": {},
    }


if __name__ == "__main__":
    sample_resume = """
    John Doe | john@example.com | github.com/johndoe

    Summary
    Software engineer with 4 years of experience in Python, Django, and REST APIs.

    Skills
    Python, JavaScript, React, SQL, PostgreSQL, Docker, Git, AWS, Agile

    Experience
    Software Engineer — TechCorp (2020–2024)
    - Built and deployed 3 microservices using Python and FastAPI, reducing latency by 40%
    - Integrated third-party APIs improving data processing speed by 25%
    - Led a team of 4 developers using Scrum methodology

    Projects
    Resume ATS Tool — Developed an ATS scorer using Python, achieving 90% keyword accuracy
    E-commerce API — Built REST API with Django and PostgreSQL for 10k+ daily users

    Education
    B.Sc. Computer Science — State University (2020)
    """

    sample_jd = """
    We are looking for a Backend Software Engineer with strong Python skills.
    Requirements:
    - 3+ years of experience with Python and Django or FastAPI
    - Experience with PostgreSQL, Docker, and AWS
    - Familiarity with microservices and REST API design
    - Experience with CI/CD pipelines (Jenkins, GitHub Actions)
    - Strong communication and teamwork skills
    - Knowledge of Kubernetes is a plus
    """

    result = full_ats_analysis(sample_resume, sample_jd)
    print(f"\n{'='*60}")
    print(f"  FINAL ATS SCORE: {result['score']} / 100")
    print(f"{'='*60}")
    print(f"  Keyword Match:   {result['keyword_score']}%")
    print(f"  Cosine Sim:      {result['cosine_score']}%")
    print(f"  Sections:        {result['section_score']}%")
    print(f"  Achievements:    {result['achievement_score']}%")
    print(f"\n  Sections Found:  {', '.join(result['found_sections'].keys())}")
    print(f"\n  Matched KWs ({len(result['matched_keywords'])}):",
          ", ".join(k for k, _ in result['matched_keywords'][:8]))
    print(f"  Missing KWs ({len(result['missing_keywords'])}):",
          ", ".join(k for k, _ in result['missing_keywords'][:8]))
    print(f"\n  Suggestions:")
    for i, s in enumerate(result['suggestions'], 1):
        print(f"  {i}. {s}")