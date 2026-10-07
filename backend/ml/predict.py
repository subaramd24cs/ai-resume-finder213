import os
import joblib
from ml.preprocessing import clean_text
from ml.resume_matcher import calculate_similarity

_model_pipeline = None

def load_model():
    global _model_pipeline
    if _model_pipeline is None:
        model_path = os.path.join(os.path.dirname(__file__), 'saved_models', 'resume_matcher_pipeline.pkl')
        if os.path.exists(model_path):
            _model_pipeline = joblib.load(model_path)
            
def predict_match_score(raw_resume: str, raw_jd: str) -> float:
    """
    Predicts the match score using the trained model.
    If the model doesn't exist, falls back to basic cosine similarity.
    """
    load_model()
    
    clean_resume = clean_text(raw_resume)
    clean_jd = clean_text(raw_jd)
    
    if _model_pipeline is not None:
        # Use trained classifier probability
        combined_text = clean_resume + " " + clean_jd
        try:
            # get probability of positive class (label 1)
            prob = _model_pipeline.predict_proba([combined_text])[0][1]
            return round(prob * 100, 2)
        except Exception as e:
            print("Prediction error:", e)
    
    # Fallback if no model trained
    return calculate_similarity(clean_resume, clean_jd)
