from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Try to load sentence transformers
try:
    from sentence_transformers import SentenceTransformer, util
    semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
    HAS_SEMANTIC = True
except ImportError:
    HAS_SEMANTIC = False

def calculate_tfidf_similarity(resume_text: str, jd_text: str) -> float:
    if not resume_text or not jd_text: return 0.0
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform([jd_text, resume_text])
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(score) * 100
    except:
        return 0.0

def calculate_semantic_similarity(resume_text: str, jd_text: str) -> float:
    if not HAS_SEMANTIC or not resume_text or not jd_text:
        return calculate_tfidf_similarity(resume_text, jd_text)
    
    # We truncate strings to avoid token limits on large resumes
    emb1 = semantic_model.encode(jd_text[:2000], convert_to_tensor=True)
    emb2 = semantic_model.encode(resume_text[:2000], convert_to_tensor=True)
    cosine_scores = util.cos_sim(emb1, emb2)
    return float(cosine_scores[0][0]) * 100

def extract_years_experience(text: str) -> int:
    match = re.search(r'(\d+)\s*(?:\+)?\s*(?:years?|yrs?)', text.lower())
    if match: return int(match.group(1))
    return 0

def calculate_weighted_score(resume_text: str, jd_text: str, matching_skills: list, missing_skills: list, weights: dict = None) -> dict:
    if weights is None:
        weights = {"skills": 0.40, "semantic": 0.30, "experience": 0.20, "education": 0.10}

    # 1. Skill Match
    total_skills = len(matching_skills) + len(missing_skills)
    skill_score = (len(matching_skills) / total_skills * 100) if total_skills > 0 else 0.0

    # 2. Semantic Similarity
    tfidf_score = calculate_tfidf_similarity(resume_text, jd_text)
    semantic_score = calculate_semantic_similarity(resume_text, jd_text) if HAS_SEMANTIC else tfidf_score
    
    # 3. Experience Match
    jd_years = extract_years_experience(jd_text)
    res_years = extract_years_experience(resume_text)
    exp_score = 100.0
    if jd_years > 0:
        if res_years >= jd_years: exp_score = 100.0
        else: exp_score = (res_years / jd_years) * 100.0

    # 4. Education Match (Heuristic)
    edu_score = 80.0
    jd_lower = jd_text.lower()
    res_lower = resume_text.lower()
    if 'bachelor' in jd_lower and 'bachelor' in res_lower: edu_score = 100.0
    elif 'master' in jd_lower and 'master' in res_lower: edu_score = 100.0
    elif 'degree' in jd_lower and 'degree' in res_lower: edu_score = 90.0

    final_score = (
        (skill_score * weights["skills"]) +
        (semantic_score * weights["semantic"]) +
        (exp_score * weights["experience"]) +
        (edu_score * weights["education"])
    )

    return {
        "final_score": round(final_score, 2),
        "skill_score": round(skill_score, 2),
        "semantic_score": round(semantic_score, 2),
        "tfidf_score": round(tfidf_score, 2),
        "experience_score": round(exp_score, 2),
        "education_score": round(edu_score, 2)
    }

