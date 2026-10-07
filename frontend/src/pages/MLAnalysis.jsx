import React, { useState, useEffect } from 'react';
import { Target, Activity, Zap, CheckCircle, Search, AlertCircle } from 'lucide-react';
import { useAuth } from '../AuthContext';

export default function MLAnalysis({ addToast }) {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { token } = useAuth();

  useEffect(() => {
    fetch('http://localhost:8000/api/ml/evaluation', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          setMetrics(data.data);
        } else {
          setError(data.message || 'Failed to load metrics');
          if (addToast) addToast(data.message || 'Failed to load metrics', 'error');
        }
        setLoading(false);
      })
      .catch(err => {
        setError('Error connecting to backend API');
        if (addToast) addToast('Error connecting to backend API', 'error');
        setLoading(false);
      });
  }, [token, addToast]);

  if (loading) {
    return (
      <div style={{textAlign: 'center', marginTop: '4rem'}}>
        <div className="loader"></div>
        <h2>Loading ML Evaluation Data...</h2>
      </div>
    );
  }

  return (
    <div>
      <h2 style={{marginBottom: '1.5rem', color: 'var(--primary-color)'}}>Machine Learning Model Analysis</h2>
      
      {error && !addToast && (
        <div style={{background: '#fed7d7', color: '#742a2a', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
          <AlertCircle size={20}/> {error}
        </div>
      )}

      {/* Model Overview */}
      <div className="card" style={{marginBottom: '2rem'}}>
        <h3 style={{marginBottom: '1rem', borderBottom: '2px solid #e2e8f0', paddingBottom: '0.5rem'}}>Model Architecture & Weights</h3>
        <p style={{fontSize: '1.05rem', lineHeight: 1.6, color: 'var(--text-dark)', marginBottom: '1.5rem'}}>
          The AI Resume Finder matching engine uses a deterministic multi-factor weighted algorithm combining deep semantic understanding with explicit requirement extraction.
        </p>
        
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem'}}>
          <div style={{background: '#ebf8ff', padding: '1rem', borderRadius: '8px', borderLeft: '4px solid #3182ce'}}>
            <div style={{fontWeight: 600, color: '#2b6cb0', marginBottom: '0.25rem', fontSize: '1.1rem'}}>40% Skill Match</div>
            <p style={{fontSize: '0.9rem', color: '#2c5282'}}>Explicit keyword and entity extraction from the text.</p>
          </div>
          <div style={{background: '#e6fffa', padding: '1rem', borderRadius: '8px', borderLeft: '4px solid #319795'}}>
            <div style={{fontWeight: 600, color: '#285e61', marginBottom: '0.25rem', fontSize: '1.1rem'}}>30% Semantic Similarity</div>
            <p style={{fontSize: '0.9rem', color: '#234e52'}}>Deep learning text embeddings (Sentence Transformers / TF-IDF).</p>
          </div>
          <div style={{background: '#fffaf0', padding: '1rem', borderRadius: '8px', borderLeft: '4px solid #dd6b20'}}>
            <div style={{fontWeight: 600, color: '#9c4221', marginBottom: '0.25rem', fontSize: '1.1rem'}}>20% Experience Match</div>
            <p style={{fontSize: '0.9rem', color: '#7b341e'}}>Calculated ratio of candidate years vs required years.</p>
          </div>
          <div style={{background: '#faf5ff', padding: '1rem', borderRadius: '8px', borderLeft: '4px solid #805ad5'}}>
            <div style={{fontWeight: 600, color: '#553c9a', marginBottom: '0.25rem', fontSize: '1.1rem'}}>10% Education Match</div>
            <p style={{fontSize: '0.9rem', color: '#44337a'}}>Degree level prerequisites and academic alignment.</p>
          </div>
        </div>
      </div>

      {/* Dataset Evaluation Metrics */}
      {metrics && (
        <div className="card">
          <h3 style={{marginBottom: '1rem', borderBottom: '2px solid #e2e8f0', paddingBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <Activity size={22} color="var(--primary-color)" /> Dataset Evaluation Metrics
          </h3>
          <p style={{fontSize: '0.95rem', color: 'var(--text-light)', marginBottom: '2rem'}}>
            These metrics reflect the performance of the underlying classifier when trained on the historical dataset `resume_dataset.csv`.
          </p>

          <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '2rem'}}>
            <div style={{textAlign: 'center', padding: '1.5rem', background: '#f7fafc', borderRadius: '8px', border: '1px solid #e2e8f0'}}>
              <Target size={32} color="#3182ce" style={{margin: '0 auto 0.5rem'}}/>
              <div style={{fontSize: '2rem', fontWeight: 700, color: '#2d3748'}}>{(metrics.accuracy * 100).toFixed(1)}%</div>
              <div style={{color: 'var(--text-light)', fontWeight: 500}}>Accuracy</div>
            </div>
            
            <div style={{textAlign: 'center', padding: '1.5rem', background: '#f7fafc', borderRadius: '8px', border: '1px solid #e2e8f0'}}>
              <CheckCircle size={32} color="#38a169" style={{margin: '0 auto 0.5rem'}}/>
              <div style={{fontSize: '2rem', fontWeight: 700, color: '#2d3748'}}>{(metrics.precision * 100).toFixed(1)}%</div>
              <div style={{color: 'var(--text-light)', fontWeight: 500}}>Precision</div>
            </div>

            <div style={{textAlign: 'center', padding: '1.5rem', background: '#f7fafc', borderRadius: '8px', border: '1px solid #e2e8f0'}}>
              <Search size={32} color="#dd6b20" style={{margin: '0 auto 0.5rem'}}/>
              <div style={{fontSize: '2rem', fontWeight: 700, color: '#2d3748'}}>{(metrics.recall * 100).toFixed(1)}%</div>
              <div style={{color: 'var(--text-light)', fontWeight: 500}}>Recall</div>
            </div>

            <div style={{textAlign: 'center', padding: '1.5rem', background: '#f7fafc', borderRadius: '8px', border: '1px solid #e2e8f0'}}>
              <Zap size={32} color="#805ad5" style={{margin: '0 auto 0.5rem'}}/>
              <div style={{fontSize: '2rem', fontWeight: 700, color: '#2d3748'}}>{(metrics.f1_score * 100).toFixed(1)}%</div>
              <div style={{color: 'var(--text-light)', fontWeight: 500}}>F1-Score</div>
            </div>
          </div>

          <div>
            <h4 style={{marginBottom: '1rem'}}>Confusion Matrix</h4>
            {metrics.confusion_matrix && (
              <div style={{maxWidth: '400px'}}>
                <table style={{width: '100%', borderCollapse: 'collapse', textAlign: 'center'}}>
                  <thead>
                    <tr>
                      <th style={{padding: '0.75rem', border: '1px solid #e2e8f0', background: '#f7fafc'}}></th>
                      <th style={{padding: '0.75rem', border: '1px solid #e2e8f0', background: '#f7fafc'}}>Predicted Negative</th>
                      <th style={{padding: '0.75rem', border: '1px solid #e2e8f0', background: '#f7fafc'}}>Predicted Positive</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <th style={{padding: '0.75rem', border: '1px solid #e2e8f0', background: '#f7fafc'}}>Actual Negative</th>
                      <td style={{padding: '1rem', border: '1px solid #e2e8f0', background: metrics.confusion_matrix[0][0] > 0 ? '#ebf8ff' : '#fff', fontWeight: 600}}>
                        {metrics.confusion_matrix[0][0]} (TN)
                      </td>
                      <td style={{padding: '1rem', border: '1px solid #e2e8f0', background: metrics.confusion_matrix[0][1] > 0 ? '#fed7d7' : '#fff', fontWeight: 600}}>
                        {metrics.confusion_matrix[0][1]} (FP)
                      </td>
                    </tr>
                    <tr>
                      <th style={{padding: '0.75rem', border: '1px solid #e2e8f0', background: '#f7fafc'}}>Actual Positive</th>
                      <td style={{padding: '1rem', border: '1px solid #e2e8f0', background: metrics.confusion_matrix[1][0] > 0 ? '#fed7d7' : '#fff', fontWeight: 600}}>
                        {metrics.confusion_matrix[1][0]} (FN)
                      </td>
                      <td style={{padding: '1rem', border: '1px solid #e2e8f0', background: metrics.confusion_matrix[1][1] > 0 ? '#c6f6d5' : '#fff', fontWeight: 600}}>
                        {metrics.confusion_matrix[1][1]} (TP)
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
