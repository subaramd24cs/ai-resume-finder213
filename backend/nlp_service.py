import os
from resume_parser import parse_resume
from ml.model import process_single_resume
from ml.ranking import rank_candidates

async def process_resumes(job_description: str, files: list) -> list:
    candidates = []
    
    for idx, file in enumerate(files):
        # Save temp file
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())
            
        # Extract text and details using existing parser
        parsed_data = parse_resume(temp_path)
        os.remove(temp_path)
        
        # Determine candidate basic info
        raw_text = parsed_data.get('text', '')
        candidate_name = parsed_data.get('name', f"Candidate {idx+1}")
        candidate_email = parsed_data.get('email', f"candidate{idx+1}@example.com")
        
        # Run ML Pipeline
        candidate_result = process_single_resume(
            raw_resume_text=raw_text,
            raw_jd_text=job_description,
            candidate_name=candidate_name,
            candidate_email=candidate_email
        )
        
        candidate_result['id'] = idx + 1
        candidates.append(candidate_result)
        
    # Rank all candidates based on their match_score
    ranked_candidates = rank_candidates(candidates)
        
    # Need to normalize keys for the frontend
    # rename 'candidate_name' back to 'name'
    for c in ranked_candidates:
        c['name'] = c.pop('candidate_name')
        
    return ranked_candidates
