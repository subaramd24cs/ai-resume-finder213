import re
from ml.skill_extractor import extract_skills

def analyze_job_description(jd_text: str) -> dict:
    """
    Extracts key requirements from a Job Description.
    """
    jd_lower = jd_text.lower()
    
    # 1. Skills (Required & Preferred)
    # Simple heuristic: Split JD by "preferred" or "nice to have"
    all_skills = extract_skills(jd_text)
    
    preferred_idx = max(jd_lower.find('preferred'), jd_lower.find('nice to have'), jd_lower.find('bonus'))
    if preferred_idx != -1:
        required_text = jd_text[:preferred_idx]
        preferred_text = jd_text[preferred_idx:]
        required_skills = extract_skills(required_text)
        preferred_skills = extract_skills(preferred_text)
    else:
        required_skills = all_skills
        preferred_skills = []
        
    # 2. Job Role / Title
    # Heuristic: First line or sentence usually contains the title
    first_line = jd_text.split('\n')[0].strip()
    job_role = first_line if len(first_line) < 60 else "Not Specified"
    
    # 3. Experience requirement
    experience = "Not Specified"
    exp_match = re.search(r'(\d+)(?:\s*-\s*\d+)?\s*\+?\s*(?:years?|yrs?)(?:\s*of)?\s*experience', jd_lower)
    if exp_match:
        experience = exp_match.group(0)
        
    # 4. Education requirement
    education = "Not Specified"
    if any(word in jd_lower for word in ['bachelor', 'bs', 'b.s']):
        education = "Bachelor's Degree"
    elif any(word in jd_lower for word in ['master', 'ms', 'm.s']):
        education = "Master's Degree"
    elif any(word in jd_lower for word in ['phd', 'ph.d']):
        education = "PhD"
        
    # 5. Certifications
    certifications = []
    certs = ['aws', 'azure', 'gcp', 'pmp', 'scrum', 'agile', 'cisco', 'ccna', 'cissp']
    for cert in certs:
        if cert in jd_lower:
            certifications.append(cert.upper())
            
    # 6. Important keywords (top 5 words not in skills/stopwords)
    words = re.findall(r'\b\w+\b', jd_lower)
    stopwords = set(['and', 'the', 'to', 'of', 'in', 'a', 'for', 'with', 'on', 'is', 'as', 'are', 'be', 'we', 'you', 'our', 'will'])
    word_freq = {}
    for w in words:
        if len(w) > 3 and w not in stopwords and w not in all_skills:
            word_freq[w] = word_freq.get(w, 0) + 1
    
    keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:8]
    keywords = [k[0] for k in keywords]
    
    return {
        "job_role": job_role,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "experience": experience,
        "education": education,
        "certifications": certifications,
        "keywords": keywords,
        "raw_text": jd_text
    }
