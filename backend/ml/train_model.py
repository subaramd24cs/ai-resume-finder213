import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from ml.preprocessing import clean_text

def train():
    # 1. Dataset loading
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset', 'resume_dataset.csv')
    df = pd.read_csv(csv_path)

    # 2. Data cleaning
    df['clean_resume'] = df['resume_text'].apply(clean_text)
    df['clean_jd'] = df['job_description'].apply(clean_text)
    
    # 3. Feature extraction
    # Concatenate resume and JD text to form a combined feature string for the model
    df['combined_text'] = df['clean_resume'] + " " + df['clean_jd']

    X = df['combined_text']
    y = df['match_label']

    # 4. Train/test split
    # Since dataset is very small, using a small test size and stratify if possible
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

    # 5. TF-IDF vectorization & 6. ML classification model
    # We create a pipeline with TF-IDF and Logistic Regression
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000, stop_words='english')),
        ('clf', LogisticRegression(random_state=42, solver='lbfgs'))
    ])

    # 7. Model training
    print("Training model...")
    pipeline.fit(X_train, y_train)

    # Save the trained model/vectorizer
    save_dir = os.path.join(os.path.dirname(__file__), 'saved_models')
    os.makedirs(save_dir, exist_ok=True)
    
    model_path = os.path.join(save_dir, 'resume_matcher_pipeline.pkl')
    joblib.dump(pipeline, model_path)
    print(f"Model saved to {model_path}")

    # Return test sets to be used by evaluation (if imported)
    return pipeline, X_test, y_test

if __name__ == "__main__":
    train()
