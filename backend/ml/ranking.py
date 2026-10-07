def generate_recommendation(score: float, matching_skills: list, missing_skills: list) -> str:
    """
    Generates a text recommendation based on the score and skills.
    """
    if score >= 75:
        return "Strong Candidate"
    elif score >= 50:
        return "Average Match"
    else:
        return "Review Needed"

def rank_candidates(candidates: list) -> list:
    """
    Sorts candidates by match_score descending and assigns a rank.
    """
    sorted_candidates = sorted(candidates, key=lambda x: x['match_score'], reverse=True)
    
    for i, candidate in enumerate(sorted_candidates):
        candidate['rank'] = i + 1
        
    return sorted_candidates
