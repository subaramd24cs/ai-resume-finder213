import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, CheckCircle, Search, Briefcase, GraduationCap, Award, Hash } from 'lucide-react';
import { useAuth } from '../AuthContext';

export default function JobDescription({ setCandidates, setIsLoading, isLoading, addToast }) {
  const [jobDescription, setJobDescription] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [jdData, setJdData] = useState(null);
  const navigate = useNavigate();
  const { token } = useAuth();

  const handleAnalyzeJD = async (e) => {
    e.preventDefault();
    if (!jobDescription.trim()) {
      if (addToast) addToast('Please enter a job description.', 'error');
      setErrorMsg('Please enter a job description.');
      return;
    }

    setIsLoading(true);
    setErrorMsg('');

    try {
      const response = await fetch('http://localhost:8000/api/jobs/analyze', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ job_description: jobDescription }),
      });
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Analysis failed');
      }

      if (data.status === 'success') {
        if (addToast) addToast('Job description analyzed successfully!', 'success');
        setJdData(data.data);
      }
    } catch (error) {
      console.error('Error:', error);
      if (addToast) addToast(error.message || 'Failed to connect to backend API', 'error');
      setErrorMsg(error.message || 'Failed to connect to backend API');
    } finally {
      setIsLoading(false);
    }
  };

  const handleMatchCandidates = async () => {
    setIsLoading(true);
    setErrorMsg('');

    try {
      const response = await fetch('http://localhost:8000/api/match', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ job_description: jobDescription }),
      });
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Match failed');
      }

      if (data.status === 'success') {
        if (addToast) addToast('Matching complete!', 'success');
        setCandidates(data.data);
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Error:', error);
      if (addToast) addToast(error.message || 'Failed to match candidates. Did you upload resumes first?', 'error');
      setErrorMsg(error.message || 'Failed to match candidates. Did you upload resumes first?');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 style={{marginBottom: '1.5rem', color: 'var(--primary-color)'}}>Step 2: Job Description Analysis</h2>
      
      {errorMsg && !addToast && (
        <div style={{background: '#fed7d7', color: '#742a2a', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
          <AlertCircle size={20}/> {errorMsg}
        </div>
      )}

      {!jdData ? (
        <form onSubmit={handleAnalyzeJD}>
          <div className="form-group">
            <label>Paste Complete Job Description</label>
            <textarea 
              className="form-control" 
              rows="10" 
              placeholder="Paste the complete job description here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
            ></textarea>
          </div>

          <button type="submit" className="btn btn-primary" disabled={isLoading} style={{width: '100%', fontSize: '1.1rem'}}>
            {isLoading ? 'Extracting Requirements...' : 'Analyze Job Description'}
          </button>
        </form>
      ) : (
        <div>
          <div style={{background: '#c6f6d5', color: '#22543d', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <CheckCircle size={20}/> Successfully Extracted Job Requirements
          </div>

          <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginBottom: '2rem'}}>
            <div style={{padding: '1rem', background: '#f7fafc', border: '1px solid #e2e8f0', borderRadius: '8px'}}>
              <h4 style={{display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-light)', marginBottom: '0.5rem'}}><Briefcase size={16}/> Job Role</h4>
              <p style={{fontWeight: 600}}>{jdData.job_role}</p>
            </div>
            
            <div style={{padding: '1rem', background: '#f7fafc', border: '1px solid #e2e8f0', borderRadius: '8px'}}>
              <h4 style={{display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-light)', marginBottom: '0.5rem'}}><Briefcase size={16}/> Experience Needed</h4>
              <p style={{fontWeight: 600}}>{jdData.experience}</p>
            </div>

            <div style={{padding: '1rem', background: '#f7fafc', border: '1px solid #e2e8f0', borderRadius: '8px'}}>
              <h4 style={{display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-light)', marginBottom: '0.5rem'}}><GraduationCap size={16}/> Education</h4>
              <p style={{fontWeight: 600}}>{jdData.education}</p>
            </div>

            <div style={{padding: '1rem', background: '#f7fafc', border: '1px solid #e2e8f0', borderRadius: '8px'}}>
              <h4 style={{display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-light)', marginBottom: '0.5rem'}}><Hash size={16}/> Keywords</h4>
              <div style={{display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.5rem'}}>
                {jdData.keywords.map((k, i) => <span key={i} className="badge" style={{background: '#e2e8f0', color: '#4a5568'}}>{k}</span>)}
              </div>
            </div>
          </div>

          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '2rem'}}>
            <div>
              <h4 style={{color: 'var(--primary-color)', marginBottom: '0.5rem'}}>Required Skills</h4>
              <ul style={{listStylePosition: 'inside', color: 'var(--text-dark)'}}>
                {jdData.required_skills.length > 0 ? jdData.required_skills.map((s, i) => <li key={i}>{s}</li>) : <li>No specific skills extracted</li>}
              </ul>
            </div>
            <div>
              <h4 style={{color: 'var(--primary-color)', marginBottom: '0.5rem'}}>Preferred Skills</h4>
              <ul style={{listStylePosition: 'inside', color: 'var(--text-dark)'}}>
                {jdData.preferred_skills.length > 0 ? jdData.preferred_skills.map((s, i) => <li key={i}>{s}</li>) : <li>No preferred skills extracted</li>}
              </ul>
            </div>
          </div>

          <div style={{display: 'flex', gap: '1rem'}}>
            <button onClick={() => setJdData(null)} className="btn" style={{background: '#e2e8f0', color: 'var(--text-dark)', flex: 1}}>
              Edit Job Description
            </button>
            <button onClick={handleMatchCandidates} className="btn btn-primary" disabled={isLoading} style={{flex: 2, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem'}}>
              {isLoading ? 'Running ML Matching...' : <><Search size={20}/> Find Best Candidates</>}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
