import React from 'react';
import { Link } from 'react-router-dom';
import { UploadCloud, FileText, BarChart2 } from 'lucide-react';

export default function Home() {
  return (
    <div>
      <div className="hero">
        <h1>Intelligent Resume Screening & Job Matching</h1>
        <p>Use Machine Learning and NLP to instantly find the best candidates for your job description.</p>
        <Link to="/upload" className="btn btn-primary">Start Analyzing Resumes</Link>
      </div>

      <div className="stats-grid" style={{marginTop: '4rem'}}>
        <div className="stat-card">
          <UploadCloud size={48} color="var(--primary-color)" style={{marginBottom: '1rem'}} />
          <h3>1. Upload Resumes</h3>
          <p style={{color: 'var(--text-light)', marginTop: '0.5rem'}}>Upload multiple PDF or DOCX resumes securely.</p>
        </div>
        <div className="stat-card">
          <FileText size={48} color="var(--primary-color)" style={{marginBottom: '1rem'}} />
          <h3>2. Add Job Description</h3>
          <p style={{color: 'var(--text-light)', marginTop: '0.5rem'}}>Enter the job requirements and desired skills.</p>
        </div>
        <div className="stat-card">
          <BarChart2 size={48} color="var(--primary-color)" style={{marginBottom: '1rem'}} />
          <h3>3. Get AI Rankings</h3>
          <p style={{color: 'var(--text-light)', marginTop: '0.5rem'}}>Our ML pipeline ranks candidates using TF-IDF & Cosine Similarity.</p>
        </div>
      </div>
    </div>
  );
}
