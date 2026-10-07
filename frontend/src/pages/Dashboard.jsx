import React, { useState, useMemo, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Filter, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';
import { useAuth } from '../AuthContext';

export default function Dashboard({ candidates: initialCandidates, isLoading: parentIsLoading, addToast }) {
  const [minScore, setMinScore] = useState(0);
  const [filterSkills, setFilterSkills] = useState('');
  const [filterExperience, setFilterExperience] = useState('');
  const [filterEducation, setFilterEducation] = useState('');
  const [filterRecommendation, setFilterRecommendation] = useState('All');
  const [sortOrder, setSortOrder] = useState('score_desc');
  const [showFilters, setShowFilters] = useState(false);
  const [candidates, setCandidates] = useState(initialCandidates || []);
  const [isLoading, setIsLoading] = useState(parentIsLoading);
  const [error, setError] = useState(null);
  const { token } = useAuth();

  useEffect(() => {
    if (initialCandidates && initialCandidates.length > 0) {
      setCandidates(initialCandidates);
      return;
    }
    
    // Fetch rankings if not provided via props
    const fetchRankings = async () => {
      setIsLoading(true);
      try {
        const res = await fetch('http://localhost:8000/api/rankings', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (res.ok && data.status === 'success') {
          setCandidates(data.data);
        } else {
          setError(data.message || 'Failed to fetch rankings');
          if (addToast) addToast(data.message || 'Failed to fetch rankings', 'error');
        }
      } catch (err) {
        setError('Error connecting to backend API');
        if (addToast) addToast('Error connecting to backend API', 'error');
      } finally {
        setIsLoading(false);
      }
    };
    fetchRankings();
  }, [initialCandidates, token, addToast]);

  if (isLoading || parentIsLoading) {
    return (
      <div style={{textAlign: 'center', marginTop: '4rem'}}>
        <div className="loader"></div>
        <h2>Loading Candidates Data...</h2>
        <p style={{color: 'var(--text-light)'}}>Fetching ML NLP pipeline results.</p>
      </div>
    );
  }

  if (!candidates || candidates.length === 0) {
    return (
      <div className="card" style={{textAlign: 'center'}}>
        <h2>No Data Available</h2>
        <p>Please upload resumes and analyze a job description first.</p>
        <Link to="/upload" className="btn btn-primary" style={{marginTop: '1rem'}}>Go to Upload</Link>
      </div>
    );
  }

  // Derived statistics
  const avgScore = candidates.reduce((acc, curr) => acc + curr.match_score, 0) / candidates.length;
  // Sort primarily to find the absolute top candidate overall
  const sortedOverall = [...candidates].sort((a, b) => b.match_score - a.match_score);
  const topCandidate = sortedOverall[0];

  // Filtering and Sorting logic
  const filteredAndSortedCandidates = useMemo(() => {
    let result = candidates.filter(c => {
      // 1. Min Score
      if (c.match_score < minScore) return false;
      
      // 2. Recommendation
      if (filterRecommendation !== 'All') {
        const score = c.match_score;
        let rec = "";
        if (score >= 80) rec = "Excellent Match";
        else if (score >= 60) rec = "Good Match";
        else if (score >= 40) rec = "Moderate Match";
        else rec = "Low Match";
        
        if (rec !== filterRecommendation) return false;
      }
      
      // 3. Skills
      if (filterSkills.trim()) {
        const query = filterSkills.toLowerCase();
        const candSkills = (c.matching_skills || []).join(' ').toLowerCase() + ' ' + (c.skills || '').toLowerCase();
        if (!candSkills.includes(query)) return false;
      }
      
      // 4. Experience
      if (filterExperience.trim()) {
        const exp = (c.experience || '').toLowerCase();
        if (!exp.includes(filterExperience.toLowerCase())) return false;
      }
      
      // 5. Education
      if (filterEducation.trim()) {
        const edu = (c.education || '').toLowerCase();
        if (!edu.includes(filterEducation.toLowerCase())) return false;
      }
      
      return true;
    });

    // Sorting
    result.sort((a, b) => {
      if (sortOrder === 'score_desc') return b.match_score - a.match_score;
      if (sortOrder === 'score_asc') return a.match_score - b.match_score;
      if (sortOrder === 'name_asc') return (a.name || a.candidate_info?.name || '').localeCompare(b.name || b.candidate_info?.name || '');
      if (sortOrder === 'name_desc') return (b.name || b.candidate_info?.name || '').localeCompare(a.name || a.candidate_info?.name || '');
      if (sortOrder === 'exp_desc') return ((b.experience || b.candidate_info?.experience) || '').localeCompare((a.experience || a.candidate_info?.experience) || ''); // simplistic string sort
      return 0;
    });

    return result;
  }, [candidates, minScore, filterSkills, filterExperience, filterEducation, filterRecommendation, sortOrder]);


  const getMatchVisuals = (score) => {
    if (score >= 80) return { label: 'Excellent Match', colorClass: 'badge-success', textColor: 'var(--success)' };
    if (score >= 60) return { label: 'Good Match', colorClass: 'badge-success', textColor: '#2b6cb0', bg: '#bee3f8' };
    if (score >= 40) return { label: 'Moderate Match', colorClass: 'badge-warning', textColor: 'var(--warning)' };
    return { label: 'Low Match', colorClass: 'badge-danger', textColor: 'var(--danger)' };
  };

  return (
    <div>
      <h2 style={{marginBottom: '1.5rem'}}>Candidate Ranking Dashboard</h2>
      
      {error && !addToast && (
        <div style={{background: '#fed7d7', color: '#742a2a', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
          <AlertCircle size={20}/> {error}
        </div>
      )}

      {/* Top Statistics */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{candidates.length}</div>
          <div className="stat-label">Total Candidates</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{filteredAndSortedCandidates.length}</div>
          <div className="stat-label">Candidates Analyzed (Filtered)</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{topCandidate.name || topCandidate.candidate_info?.name || 'Unknown'}</div>
          <div className="stat-label">Top Match ({topCandidate.match_score}%)</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{avgScore.toFixed(1)}%</div>
          <div className="stat-label">Average Match Score</div>
        </div>
      </div>

      <div className="card" style={{marginBottom: '2rem'}}>
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', cursor: 'pointer'}} onClick={() => setShowFilters(!showFilters)}>
          <h3 style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}><Filter size={20}/> Filters & Sorting</h3>
          {showFilters ? <ChevronUp size={20}/> : <ChevronDown size={20}/>}
        </div>
        
        {showFilters && (
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', padding: '1rem', background: '#f7fafc', borderRadius: '8px'}}>
            <div className="form-group" style={{marginBottom: 0}}>
              <label>Minimum Score: {minScore}%</label>
              <input type="range" min="0" max="100" value={minScore} onChange={(e) => setMinScore(e.target.value)} style={{width: '100%'}}/>
            </div>
            
            <div className="form-group" style={{marginBottom: 0}}>
              <label>Match Recommendation</label>
              <select className="form-control" value={filterRecommendation} onChange={(e) => setFilterRecommendation(e.target.value)}>
                <option value="All">All Categories</option>
                <option value="Excellent Match">Excellent Match (80-100)</option>
                <option value="Good Match">Good Match (60-79)</option>
                <option value="Moderate Match">Moderate Match (40-59)</option>
                <option value="Low Match">Low Match (Below 40)</option>
              </select>
            </div>

            <div className="form-group" style={{marginBottom: 0}}>
              <label>Filter by Skills</label>
              <input type="text" className="form-control" placeholder="e.g. Python" value={filterSkills} onChange={(e) => setFilterSkills(e.target.value)} />
            </div>

            <div className="form-group" style={{marginBottom: 0}}>
              <label>Filter by Experience</label>
              <input type="text" className="form-control" placeholder="e.g. 5 years" value={filterExperience} onChange={(e) => setFilterExperience(e.target.value)} />
            </div>

            <div className="form-group" style={{marginBottom: 0}}>
              <label>Filter by Education</label>
              <input type="text" className="form-control" placeholder="e.g. Bachelor" value={filterEducation} onChange={(e) => setFilterEducation(e.target.value)} />
            </div>

            <div className="form-group" style={{marginBottom: 0}}>
              <label>Sort By</label>
              <select className="form-control" value={sortOrder} onChange={(e) => setSortOrder(e.target.value)}>
                <option value="score_desc">Highest Score First</option>
                <option value="score_asc">Lowest Score First</option>
                <option value="name_asc">Candidate Name (A-Z)</option>
                <option value="name_desc">Candidate Name (Z-A)</option>
                <option value="exp_desc">Experience</option>
              </select>
            </div>
          </div>
        )}
      </div>

      <div className="card">
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem'}}>
          <h3>Ranked Candidates</h3>
          <span style={{color: 'var(--text-light)', fontSize: '0.9rem'}}>Showing {filteredAndSortedCandidates.length} of {candidates.length}</span>
        </div>
        
        <div className="table-responsive">
          <table className="table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Candidate</th>
                <th>Match Score</th>
                <th>Experience / Edu</th>
                <th>Matched Skills</th>
                <th>Missing Skills</th>
                <th>Recommendation</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredAndSortedCandidates.map((c, index) => {
                const visual = getMatchVisuals(c.match_score);
                const cname = c.name || c.candidate_info?.name || 'Unknown';
                const cemail = c.email || c.candidate_info?.email || 'Unknown';
                const cexp = c.experience || c.candidate_info?.experience || 'Unknown';
                const cedu = c.education || c.candidate_info?.education || 'Unknown';
                const cid = c.resume_id || c.id;
                
                return (
                  <tr key={cid || index}>
                    <td>
                      <div style={{fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-light)'}}>#{index + 1}</div>
                      {c.rank && <div style={{fontSize: '0.75rem', color: '#a0aec0'}}>Overall: #{c.rank}</div>}
                    </td>
                    <td>
                      <div style={{fontWeight: 600}}>{cname}</div>
                      <div style={{fontSize: '0.85rem', color: 'var(--text-light)'}}>{cemail}</div>
                    </td>
                    <td>
                      <div style={{fontSize: '1.25rem', fontWeight: 700, color: visual.textColor}}>
                        {c.match_score}%
                      </div>
                      <div style={{width: '100%', background: '#e2e8f0', height: '6px', borderRadius: '3px', marginTop: '4px'}}>
                        <div style={{width: `${c.match_score}%`, background: visual.bg || visual.textColor, height: '100%', borderRadius: '3px'}}></div>
                      </div>
                    </td>
                    <td>
                      <div style={{fontSize: '0.9rem'}}>{cexp !== "Not explicitly found" ? cexp.substring(0, 30) + (cexp.length > 30 ? '...' : '') : "Unknown"}</div>
                      <div style={{fontSize: '0.8rem', color: 'var(--text-light)'}}>{cedu !== "Not explicitly found" ? cedu.substring(0, 20) + (cedu.length > 20 ? '...' : '') : "Unknown Education"}</div>
                    </td>
                    <td style={{maxWidth: '200px'}}>
                      <div style={{display: 'flex', flexWrap: 'wrap', gap: '4px'}}>
                        {(c.matching_skills || []).slice(0, 3).map((s, i) => (
                          <span key={i} style={{background: '#c6f6d5', color: '#22543d', padding: '2px 6px', borderRadius: '4px', fontSize: '0.75rem'}}>{s}</span>
                        ))}
                        {(c.matching_skills || []).length > 3 && <span style={{fontSize: '0.75rem', color: 'var(--text-light)'}}>+{c.matching_skills.length - 3} more</span>}
                        {(!c.matching_skills || c.matching_skills.length === 0) && <span style={{fontSize: '0.8rem', color: 'var(--text-light)'}}>None matched</span>}
                      </div>
                    </td>
                    <td style={{maxWidth: '200px'}}>
                      <div style={{display: 'flex', flexWrap: 'wrap', gap: '4px'}}>
                        {(c.missing_skills || []).slice(0, 3).map((s, i) => (
                          <span key={i} style={{background: '#fed7d7', color: '#742a2a', padding: '2px 6px', borderRadius: '4px', fontSize: '0.75rem'}}>{s}</span>
                        ))}
                        {(c.missing_skills || []).length > 3 && <span style={{fontSize: '0.75rem', color: 'var(--text-light)'}}>+{c.missing_skills.length - 3} more</span>}
                        {(!c.missing_skills || c.missing_skills.length === 0) && <span style={{fontSize: '0.8rem', color: 'var(--text-light)'}}>None missing</span>}
                      </div>
                    </td>
                    <td>
                      <span className={`badge`} style={{background: visual.bg || visual.textColor, color: visual.textColor === 'var(--success)' ? '#fff' : (visual.bg ? '#2b6cb0' : '#fff')}}>
                        {visual.label}
                      </span>
                    </td>
                    <td>
                      <Link to={`/candidate/${cid}`} className="btn btn-primary" style={{padding: '0.4rem 0.8rem', fontSize: '0.85rem'}}>View Analysis</Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
