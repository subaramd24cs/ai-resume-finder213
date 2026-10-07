import re

# Comprehensive list of common tech skills
COMMON_SKILLS = [
    "python", "java", "javascript", "c++", "c#", "ruby", "php", "swift", "kotlin", "go",
    "rust", "typescript", "html", "css", "sql", "nosql", "mongodb", "postgresql", "mysql",
    "oracle", "redis", "docker", "kubernetes", "aws", "azure", "gcp", "linux", "unix",
    "bash", "git", "github", "gitlab", "jenkins", "ci/cd", "agile", "scrum", "machine learning",
    "deep learning", "nlp", "computer vision", "tensorflow", "keras", "pytorch", "scikit-learn",
    "pandas", "numpy", "matplotlib", "seaborn", "data science", "data analytics", "hadoop",
    "spark", "kafka", "flask", "django", "fastapi", "spring boot", "react", "angular", "vue",
    "node.js", "express", "graphql", "rest api", "soap", "microservices", "terraform", "ansible"
]

def extract_skills(text: str) -> list:
    """
    Extracts skills from text based on a predefined list of skills.
    Matches are case-insensitive.
    """
    if not text:
        return []
        
    text_lower = text.lower()
    extracted_skills = []
    
    for skill in COMMON_SKILLS:
        # Use regex to match whole words/phrases
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            extracted_skills.append(skill)
            
    return extracted_skills

def find_matching_and_missing_skills(resume_skills: list, job_skills: list) -> tuple:
    """
    Compares resume skills with job description skills to find matches and gaps.
    """
    set_resume = set(resume_skills)
    set_job = set(job_skills)
    
    matching_skills = list(set_job.intersection(set_resume))
    missing_skills = list(set_job.difference(set_resume))
    
    return matching_skills, missing_skills
