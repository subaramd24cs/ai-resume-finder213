import os
import json
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from ml.train_model import train

def evaluate():
    # 8. Model evaluation
    print("Evaluating Model...")
    pipeline, X_test, y_test = train()
    
    y_pred = pipeline.predict(X_test)
    
    # 9. Accuracy
    acc = accuracy_score(y_test, y_pred)
    # 10. Precision
    prec = precision_score(y_test, y_pred, zero_division=0)
    # 11. Recall
    rec = recall_score(y_test, y_pred, zero_division=0)
    # 12. F1-score
    f1 = f1_score(y_test, y_pred, zero_division=0)
    # 13. Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    
    metrics = {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "confusion_matrix": cm.tolist()
    }
    
    metrics_path = os.path.join(os.path.dirname(__file__), 'evaluation_metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=4)
    
    print("\n--- Evaluation Metrics ---")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print("\n--- Confusion Matrix ---")
    print(cm)
    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred, zero_division=0))

if __name__ == "__main__":
    evaluate()
