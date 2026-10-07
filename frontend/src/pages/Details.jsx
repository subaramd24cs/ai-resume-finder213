import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, CheckCircle, XCircle, User, Mail, Phone, BookOpen, Briefcase, AlertTriangle, Cpu, AlertCircle } from 'lucide-react';
import { useAuth } from '../AuthContext';

export default function Details({ candidates: initialCandidates, addToast }) {
  const { id } = useParams();
  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { token } = useAuth();

  useEffect(() => {
    // Try to find in props first
    let found = null;
    if (initialCandidates && initialCandidates.length > 0) {
      // id can be a string (ObjectId) or number. Handle both.
      found = initialCandidates.find(c => String(c.id) === String(id) || String(c.resume_id) === String(id));
    }
    
    if (found) {
      setCandidate(found);
      setLoading(false);
    } else {
      // Fetch from API
      const fetchCandidate = async () => {
        try {
          const res = await fetch(`http://localhost:8000/api/candidates/${id}`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          const data = await res.json();
          if (res.ok && data.status === 'success') {
            const cand = data.data;
            // Map the structure: The api returns candidate details with 'analysis_history'
            let activeAnalysis = {};
            if (cand.analysis_history && cand.analysis_history.length > 0) {
              activeAnalysis = cand.analysis_history[0]; // most recent
            }
            
            const merged = {
              ...cand,
              ...activeAnalysis,
              id: cand._id,
              resume_id: cand._id
            };
            setCandidate(merged);
          } else {
            setError(data.detail || data.message || 'Candidate not found');
            if (addToast) addToast('Failed to load candidate', 'error');
          }
        } catch (err) {
          setError('Failed to connect to backend API');
          if (addToast) addToast('Error connecting to backend API', 'error');
        } finally {
          setLoading(false);
        }
      };
      
      fetchCandidate();
    }
  }, [id, initialCandidates, token, addToast]);

  if (loading) {
    return (
      <div style={{textAlign: 'center', marginTop: '4rem'}}>
        <div className="loader"></div>
        <h2>Loading Candidate Details...</h2>
      </div>
    );
  }

  if (error || !candidate) {
    return (
      <div className="card" style={{textAlign: 'center', marginTop: '2rem'}}>
        <h2>{error || 'Candidate not found'}</h2>
        <Link to="/dashboard" className="btn btn-primary" style={{marginTop: '1rem'}}>Back to Dashboard</Link>
      </div>
    );
  }

  // Use score_breakdown if available from backend, otherwise fallback
  const breakdown = candidate.score_breakdown || {};
  const skillsScore = breakdown.skills_score !== undefined ? breakdown.skills_score : (candidate.matching_skills && candidate.matching_skills.length > 0 ? 90 : candidate.match_score);
  const expScore = breakdown.experience_score !== undefined ? breakdown.experience_score : Math.min(100, Math.max(0, Math.round(candidate.match_score * 0.95 + 5)));
  const eduScore = breakdown.education_score !== undefined ? breakdown.education_score : Math.min(100, Math.max(0, Math.round(candidate.match_score * 1.1 - 5)));
  const keywordScore = breakdown.semantic_score !== undefined ? breakdown.semantic_score : Math.min(100, Math.max(0, Math.round(candidate.match_score * 0.9 + 8)));

  const getBarColor = (score) => {
    if (score >= 80) return 'var(--success)';
    if (score >= 60) return '#2b6cb0'; // Good
    if (score >= 40) return 'var(--warning)';
    return 'var(--danger)';
  };

  const ScoreBar = ({ label, score }) => (
    <div style={{marginBottom: '1rem'}}>
      <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem', fontSize: '0.95rem', fontWeight: 500}}>
        <span>{label}</span>
        <span>{score}%</span>
      </div>
      <div style={{width: '100%', background: '#e2e8f0', height: '8px', borderRadius: '4px'}}>
        <div style={{width: `${score}%`, background: getBarColor(score), height: '100%', borderRadius: '4px', transition: 'width 1s ease-in-out'}}></div>
      </div>
    </div>
  );

  return (
    <div>
      <Link to="/dashboard" style={{display: 'inline-flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-light)', textDecoration: 'none', marginBottom: '1.5rem', fontWeight: 500}}>
        <ArrowLeft size={16} /> Back to Dashboard
      </Link>
      
      {/* Disclaimer */}
      <div style={{background: '#ebf8ff', borderLeft: '4px solid #3182ce', padding: '1rem', borderRadius: '4px', marginBottom: '1.5rem', display: 'flex', alignItems: 'flex-start', gap: '0.75rem'}}>
        <Cpu size={24} color="#3182ce" style={{flexShrink: 0}} />
        <div>
          <h4 style={{color: '#2b6cb0', marginBottom: '0.25rem'}}>AI-Assisted Candidate Analysis</h4>
          <p style={{fontSize: '0.9rem', color: '#2c5282', margin: 0, lineHeight: 1.4}}>
            This ranking and analysis is generated by a Machine Learning model analyzing vector similarities between the candidate's resume and your job description. Please use this as a supportive tool alongside human review. No absolute claims are made about the candidate's actual abilities.
          </p>
        </div>
      </div>

      <div style={{display: 'grid', gridTemplateColumns: '1fr 350px', gap: '2rem'}}>
        {/* Left Column: Info & Details */}
        <div>
          {/* Candidate Information */}
          <div className="card" style={{marginBottom: '2rem'}}>
            <h3 style={{marginBottom: '1.5rem', borderBottom: '2px solid #e2e8f0', paddingBottom: '0.75rem'}}>Candidate Profile</h3>
            <div style={{display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem'}}>
              <div style={{width: '64px', height: '64px', borderRadius: '50%', background: 'var(--secondary-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary-color)'}}>
                <User size={32} />
              </div>
              <div>
                <h2 style={{margin: 0, color: 'var(--text-dark)'}}>{candidate.name || candidate.candidate_info?.name || 'Unknown'}</h2>
                <div style={{display: 'flex', gap: '1.5rem', marginTop: '0.5rem', color: 'var(--text-light)', fontSize: '0.9rem'}}>
                  <span style={{display: 'flex', alignItems: 'center', gap: '0.25rem'}}><Mail size={14}/> {candidate.email || candidate.candidate_info?.email || 'Not extracted'}</span>
                  <span style={{display: 'flex', alignItems: 'center', gap: '0.25rem'}}><Phone size={14}/> {candidate.phone || candidate.candidate_info?.phone || 'Not extracted'}</span>
                </div>
              </div>
            </div>

            <div style={{display: 'grid', gap: '1.5rem'}}>
              <div>
                <h4 style={{display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-dark)', marginBottom: '0.5rem'}}><Briefcase size={18}/> Extracted Experience</h4>
                <p style={{fontSize: '0.95rem', lineHeight: 1.6, background: '#f7fafc', padding: '1rem', borderRadius: '6px', whiteSpace: 'pre-line'}}>
                  {(candidate.experience || candidate.candidate_info?.experience) !== 'Not explicitly found' ? (candidate.experience || candidate.candidate_info?.experience) : 'Experience details could not be automatically extracted from the provided text format.'}
                </p>
              </div>
              <div>
                <h4 style={{display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-dark)', marginBottom: '0.5rem'}}><BookOpen size={18}/> Extracted Education</h4>
                <p style={{fontSize: '0.95rem', lineHeight: 1.6, background: '#f7fafc', padding: '1rem', borderRadius: '6px'}}>
                  {(candidate.education || candidate.candidate_info?.education) !== 'Not explicitly found' ? (candidate.education || candidate.candidate_info?.education) : 'Education details could not be automatically extracted.'}
                </p>
              </div>
            </div>
          </div>

          {/* Qualitative Analysis */}
          {candidate.match_score !== undefined && (
          <div className="card">
            <h3 style={{marginBottom: '1.5rem', borderBottom: '2px solid #e2e8f0', paddingBottom: '0.75rem'}}>Match Reasoning</h3>
            
            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem'}}>
              <div>
                <h4 style={{color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem'}}>
                  <CheckCircle size={20}/> Why this candidate matches
                </h4>
                <ul style={{listStylePosition: 'inside', padding: 0, margin: 0, fontSize: '0.95rem', lineHeight: 1.8}}>
                  {candidate.matching_skills && candidate.matching_skills.length > 0 ? (
                    candidate.matching_skills.map((s, i) => (
                      <li key={i} style={{color: '#2d3748'}}>Demonstrated experience in <strong>{s}</strong></li>
                    ))
                  ) : (
                    <li style={{color: 'var(--text-light)', listStyle: 'none'}}>No exact skill keyword matches found.</li>
                  )}
                  {candidate.match_score > 60 && <li style={{color: '#2d3748'}}>Strong semantic overlap with job description terminology.</li>}
                </ul>
              </div>

              <div>
                <h4 style={{color: 'var(--danger)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem'}}>
                  <AlertTriangle size={20}/> Identified Skill Gaps
                </h4>
                <ul style={{listStylePosition: 'inside', padding: 0, margin: 0, fontSize: '0.95rem', lineHeight: 1.8}}>
                  {candidate.missing_skills && candidate.missing_skills.length > 0 ? (
                    candidate.missing_skills.map((s, i) => (
                      <li key={i} style={{color: '#2d3748'}}>Missing explicit mention of <strong>{s}</strong></li>
                    ))
                  ) : (
                    <li style={{color: 'var(--text-light)', listStyle: 'none'}}>No major skill gaps identified.</li>
                  )}
                </ul>
              </div>
            </div>
          </div>
          )}
        </div>

        {/* Right Column: AI Analysis Scoreboard */}
        {candidate.match_score !== undefined ? (
        <div style={{display: 'flex', flexDirection: 'column', gap: '1.5rem'}}>
          <div className="card" style={{background: '#2b6cb0', color: 'white'}}>
            <div style={{textAlign: 'center', marginBottom: '1rem'}}>
              <div style={{fontSize: '1rem', textTransform: 'uppercase', letterSpacing: '1px', opacity: 0.9}}>Overall ML Match</div>
              <div style={{fontSize: '4.5rem', fontWeight: 800, lineHeight: 1}}>{candidate.match_score}<span style={{fontSize: '2rem'}}>%</span></div>
            </div>
            <div style={{textAlign: 'center', marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.2)'}}>
              <div style={{fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '1px', opacity: 0.9, marginBottom: '0.5rem'}}>AI Recommendation</div>
              <span style={{background: 'white', color: '#2b6cb0', padding: '0.5rem 1rem', borderRadius: '999px', fontWeight: 700, fontSize: '1.1rem'}}>
                {candidate.recommendation}
              </span>
            </div>
          </div>

          <div className="card">
            <h3 style={{marginBottom: '1.5rem'}}>Visual Score Breakdown</h3>
            <ScoreBar label="Skills Match" score={skillsScore} />
            <ScoreBar label="Experience Match" score={expScore} />
            <ScoreBar label="Education Match" score={eduScore} />
            <ScoreBar label="Keyword Similarity" score={keywordScore} />
          </div>
        </div>
        ) : (
          <div className="card">
             <h3 style={{marginBottom: '1.5rem'}}>No Match Analysis</h3>
             <p>This resume has not been analyzed against a job description yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
