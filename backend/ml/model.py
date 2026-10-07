from .skill_extractor import extract_skills, find_matching_and_missing_skills
from .ranking import generate_recommendation
from .resume_matcher import calculate_weighted_score

def process_single_resume(raw_resume_text: str, raw_jd_text: str, candidate_name: str = "Unknown", candidate_email: str = "unknown@example.com") -> dict:
    """
    Complete ML pipeline for a single resume against a job description.
    """
    
    # 1. Extract Skills
    resume_skills = extract_skills(raw_resume_text)  # Use raw text to catch uncleaned variants
    jd_skills = extract_skills(raw_jd_text)
    
    # 2. Find matching and missing skills
    matching_skills, missing_skills = find_matching_and_missing_skills(resume_skills, jd_skills)
    
    # 3. Use the deterministic weighted matching model
    scores = calculate_weighted_score(
        resume_text=raw_resume_text, 
        jd_text=raw_jd_text, 
        matching_skills=matching_skills, 
        missing_skills=missing_skills
    )
    
    match_score = scores["final_score"]
    
    # 4. Generate Recommendation
    recommendation = generate_recommendation(match_score, matching_skills, missing_skills)
    
    # Construct final candidate profile
    return {
        "candidate_name": candidate_name,
        "email": candidate_email,
        "match_score": match_score,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "experience": "Not Extracted", # Set by main.py
        "education": "Not Extracted", # Set by main.py
        "recommendation": recommendation,
        "skills": ", ".join(resume_skills) if resume_skills else "No obvious skills detected",
        # Keep score breakdown for analysis
        "score_breakdown": scores
    }
