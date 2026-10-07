import os

def create_files(base_dir, structure):
    for name, content in structure.items():
        path = os.path.join(base_dir, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_files(path, content)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

backend_files = {
    'requirements.txt': '''fastapi
uvicorn
pymongo
scikit-learn
pandas
numpy
nltk
spacy
python-multipart
pdfplumber
docx2txt
pydantic
motor
''',
    'main.py': '''from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn
from nlp_service import process_resumes
from database import get_db

app = FastAPI(title="AI Resume Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Resume Finder API"}

@app.post("/api/analyze")
async def analyze_resumes(job_description: str = Form(...), files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No resumes uploaded")
    
    results = await process_resumes(job_description, files)
    
    # Save to MongoDB
    # db = get_db()
    # if db is not None:
    #     for result in results:
    #         db.candidates.insert_one(result)
            
    return {"status": "success", "data": results}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
''',
    'database.py': '''from pymongo import MongoClient
import os

def get_db():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        return client.resume_finder_db
    except Exception as e:
        print("Could not connect to MongoDB:", e)
        return None
''',
    'nlp_service.py': '''import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from resume_parser import parse_resume

async def process_resumes(job_description, files):
    candidates = []
    
    for idx, file in enumerate(files):
        # Save temp file
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())
            
        # Extract text and details
        parsed_data = parse_resume(temp_path)
        os.remove(temp_path)
        
        # Calculate matching score using TF-IDF and Cosine Similarity
        documents = [job_description, parsed_data['text']]
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf_matrix = vectorizer.fit_transform(documents)
            score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            score_percentage = round(score * 100, 2)
        except:
            score_percentage = 0.0
            
        # Basic mock logic for skills extraction
        job_skills = set(job_description.lower().split())
        resume_skills = set(parsed_data['text'].lower().split())
        
        matched_skills = list(job_skills.intersection(resume_skills))[:5]
        missing_skills = list(job_skills.difference(resume_skills))[:5]
        
        candidate = {
            "id": idx + 1,
            "name": parsed_data.get('name', f"Candidate {idx+1}"),
            "email": parsed_data.get('email', f"candidate{idx+1}@example.com"),
            "skills": ", ".join(matched_skills) if matched_skills else "Various skills",
            "experience": "2-5 years", # Mocked for now
            "match_score": score_percentage,
            "matching_skills": matched_skills,
            "missing_skills": missing_skills,
            "recommendation": "Highly Recommended" if score_percentage > 70 else "Review Needed"
        }
        candidates.append(candidate)
        
    # Sort by match score descending
    candidates.sort(key=lambda x: x['match_score'], reverse=True)
    
    # Reassign ranks
    for i, c in enumerate(candidates):
        c['rank'] = i + 1
        
    return candidates
''',
    'resume_parser.py': '''import pdfplumber
import docx2txt

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
    except Exception as e:
        print("Error reading PDF:", e)
    return text

def extract_text_from_docx(docx_path):
    try:
        text = docx2txt.process(docx_path)
        return text
    except Exception as e:
        print("Error reading DOCX:", e)
        return ""

def parse_resume(file_path):
    ext = file_path.split('.')[-1].lower()
    text = ""
    if ext == 'pdf':
        text = extract_text_from_pdf(file_path)
    elif ext in ['doc', 'docx']:
        text = extract_text_from_docx(file_path)
        
    # We could use spaCy/NLTK here for NER (Named Entity Recognition) to get names, emails, etc.
    # For now, we return basic extracted text
    return {
        "text": text,
        "name": "Extracted Name", # In a real implementation use regex/NLP
        "email": "extracted@email.com"
    }
'''
}

frontend_files = {
    'package.json': '''{
  "name": "ai-resume-finder",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.6.2",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.1",
    "lucide-react": "^0.294.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "@vitejs/plugin-react": "^4.2.0",
    "eslint": "^8.53.0",
    "eslint-plugin-react": "^7.33.2",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.4",
    "vite": "^5.0.0"
  }
}
''',
    'vite.config.js': '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
})
''',
    'index.html': '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI Resume Finder</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
''',
    'src': {
        'main.jsx': '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
''',
        'App.css': '''
:root {
  --primary-color: #0f4c81; /* Classic Blue */
  --secondary-color: #e1e8f0;
  --accent-color: #00a8ff;
  --text-dark: #2d3748;
  --text-light: #718096;
  --bg-color: #f7fafc;
  --white: #ffffff;
  --success: #38a169;
  --warning: #d69e2e;
  --danger: #e53e3e;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Inter', sans-serif;
  background-color: var(--bg-color);
  color: var(--text-dark);
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Navbar */
.navbar {
  background-color: var(--white);
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
  text-decoration: none;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
}

.nav-links a {
  text-decoration: none;
  color: var(--text-light);
  font-weight: 500;
  transition: color 0.3s;
}

.nav-links a:hover, .nav-links a.active {
  color: var(--primary-color);
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

/* Home */
.hero {
  text-align: center;
  padding: 4rem 2rem;
  background: linear-gradient(135deg, var(--primary-color), #2b6cb0);
  color: var(--white);
  border-radius: 12px;
  margin-bottom: 2rem;
}

.hero h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.hero p {
  font-size: 1.2rem;
  opacity: 0.9;
  margin-bottom: 2rem;
}

.btn {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.btn-primary {
  background-color: var(--accent-color);
  color: var(--white);
}

.btn-primary:hover {
  background-color: #0097e6;
  transform: translateY(-2px);
}

/* Form */
.card {
  background: var(--white);
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--text-dark);
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #cbd5e0;
  border-radius: 6px;
  font-family: inherit;
  font-size: 1rem;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(15, 76, 129, 0.1);
}

/* File Upload */
.file-upload {
  border: 2px dashed #cbd5e0;
  padding: 2rem;
  text-align: center;
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.3s;
}

.file-upload:hover {
  border-color: var(--primary-color);
}

/* Dashboard Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--white);
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  text-align: center;
  border-bottom: 4px solid var(--primary-color);
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary-color);
}

.stat-label {
  color: var(--text-light);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Table */
.table-responsive {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th, .table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.table th {
  background-color: #f7fafc;
  font-weight: 600;
  color: var(--text-light);
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
}

.badge-success { background: #c6f6d5; color: #22543d; }
.badge-warning { background: #feebc8; color: #7b341e; }
.badge-danger { background: #fed7d7; color: #742a2a; }

.match-score {
  font-weight: 700;
}

.score-high { color: var(--success); }
.score-med { color: var(--warning); }
.score-low { color: var(--danger); }

/* Footer */
.footer {
  background: var(--white);
  text-align: center;
  padding: 1.5rem;
  color: var(--text-light);
  border-top: 1px solid #e2e8f0;
}

/* Loader */
.loader {
  border: 4px solid #f3f3f3;
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 2rem auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
''',
        'index.css': '''
@import './App.css';
''',
        'App.jsx': '''import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import Home from './pages/Home';
import Upload from './pages/Upload';
import Dashboard from './pages/Dashboard';
import Details from './pages/Details';
import About from './pages/About';
import { Search, UploadCloud, LayoutDashboard, Info } from 'lucide-react';
import './App.css';

function App() {
  const [candidates, setCandidates] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  return (
    <Router>
      <div className="app-container">
        <nav className="navbar">
          <Link to="/" className="navbar-brand">
            <Search size={24} />
            AI Resume Finder
          </Link>
          <div className="nav-links">
            <Link to="/"><LayoutDashboard size={18}/> Home</Link>
            <Link to="/upload"><UploadCloud size={18}/> Upload</Link>
            <Link to="/dashboard"><LayoutDashboard size={18}/> Dashboard</Link>
            <Link to="/about"><Info size={18}/> About</Link>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/upload" element={<Upload setCandidates={setCandidates} setIsLoading={setIsLoading} isLoading={isLoading} />} />
            <Route path="/dashboard" element={<Dashboard candidates={candidates} isLoading={isLoading} />} />
            <Route path="/candidate/:id" element={<Details candidates={candidates} />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>

        <footer className="footer">
          <p>&copy; {new Date().getFullYear()} AI Resume Finder. ML-Powered Job Matching System.</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
''',
        'pages': {
            'Home.jsx': '''import React from 'react';
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
''',
            'Upload.jsx': '''import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload as UploadIcon, File } from 'lucide-react';

export default function Upload({ setCandidates, setIsLoading, isLoading }) {
  const [jobDescription, setJobDescription] = useState('');
  const [files, setFiles] = useState([]);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!jobDescription || files.length === 0) {
      alert('Please provide a job description and at least one resume.');
      return;
    }

    setIsLoading(true);
    navigate('/dashboard');

    const formData = new FormData();
    formData.append('job_description', jobDescription);
    files.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (data.status === 'success') {
        setCandidates(data.data);
      } else {
        alert('Analysis failed');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to connect to backend API');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 style={{marginBottom: '1.5rem', color: 'var(--primary-color)'}}>Upload & Analyze</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Job Description</label>
          <textarea 
            className="form-control" 
            rows="6" 
            placeholder="Paste the complete job description here..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          ></textarea>
        </div>

        <div className="form-group">
          <label>Upload Resumes (PDF, DOCX)</label>
          <label className="file-upload" htmlFor="resume-upload">
            <UploadIcon size={32} color="var(--text-light)" style={{marginBottom: '0.5rem'}} />
            <p>Click or drag files here to upload</p>
            <input 
              type="file" 
              id="resume-upload" 
              multiple 
              accept=".pdf,.doc,.docx"
              style={{display: 'none'}}
              onChange={handleFileChange}
            />
          </label>
          {files.length > 0 && (
            <div style={{marginTop: '1rem'}}>
              <p style={{fontWeight: 600}}>Selected Files:</p>
              <ul style={{listStyle: 'none'}}>
                {files.map((f, i) => (
                  <li key={i} style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.5rem'}}>
                    <File size={16} /> {f.name}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <button type="submit" className="btn btn-primary" disabled={isLoading} style={{width: '100%', fontSize: '1.1rem'}}>
          {isLoading ? 'Analyzing...' : 'Run ML Analysis'}
        </button>
      </form>
    </div>
  );
}
''',
            'Dashboard.jsx': '''import React from 'react';
import { Link } from 'react-router-dom';

export default function Dashboard({ candidates, isLoading }) {
  if (isLoading) {
    return (
      <div style={{textAlign: 'center', marginTop: '4rem'}}>
        <div className="loader"></div>
        <h2>Running ML NLP Pipeline...</h2>
        <p style={{color: 'var(--text-light)'}}>Extracting text, computing TF-IDF vectors, and calculating cosine similarities.</p>
      </div>
    );
  }

  if (!candidates || candidates.length === 0) {
    return (
      <div className="card" style={{textAlign: 'center'}}>
        <h2>No Data Available</h2>
        <p>Please go to the upload page to analyze resumes.</p>
        <Link to="/upload" className="btn btn-primary" style={{marginTop: '1rem'}}>Go to Upload</Link>
      </div>
    );
  }

  const avgScore = candidates.reduce((acc, curr) => acc + curr.match_score, 0) / candidates.length;
  const topCandidate = candidates[0];

  return (
    <div>
      <h2 style={{marginBottom: '1.5rem'}}>Analysis Dashboard</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{candidates.length}</div>
          <div className="stat-label">Resumes Analyzed</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{avgScore.toFixed(1)}%</div>
          <div className="stat-label">Avg Match Score</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{topCandidate.name}</div>
          <div className="stat-label">Top Candidate</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{topCandidate.match_score}%</div>
          <div className="stat-label">Top Score</div>
        </div>
      </div>

      <div className="card">
        <h3 style={{marginBottom: '1rem'}}>Candidate Rankings</h3>
        <div className="table-responsive">
          <table className="table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Candidate Name</th>
                <th>Match Score</th>
                <th>Experience</th>
                <th>Recommendation</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((c) => (
                <tr key={c.id}>
                  <td><strong>#{c.rank}</strong></td>
                  <td>
                    <div style={{fontWeight: 600}}>{c.name}</div>
                    <div style={{fontSize: '0.85rem', color: 'var(--text-light)'}}>{c.email}</div>
                  </td>
                  <td>
                    <span className={`match-score ${c.match_score >= 70 ? 'score-high' : c.match_score >= 40 ? 'score-med' : 'score-low'}`}>
                      {c.match_score}%
                    </span>
                  </td>
                  <td>{c.experience}</td>
                  <td>
                    <span className={`badge ${c.match_score >= 70 ? 'badge-success' : c.match_score >= 40 ? 'badge-warning' : 'badge-danger'}`}>
                      {c.recommendation}
                    </span>
                  </td>
                  <td>
                    <Link to={`/candidate/${c.id}`} style={{color: 'var(--accent-color)', fontWeight: 600, textDecoration: 'none'}}>View Details</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
''',
            'Details.jsx': '''import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, CheckCircle, XCircle } from 'lucide-react';

export default function Details({ candidates }) {
  const { id } = useParams();
  const candidate = candidates.find(c => c.id === parseInt(id));

  if (!candidate) {
    return <div>Candidate not found</div>;
  }

  return (
    <div>
      <Link to="/dashboard" style={{display: 'inline-flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-light)', textDecoration: 'none', marginBottom: '1.5rem'}}>
        <ArrowLeft size={16} /> Back to Dashboard
      </Link>
      
      <div className="card">
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem'}}>
          <div>
            <h1>{candidate.name}</h1>
            <p style={{color: 'var(--text-light)', fontSize: '1.1rem'}}>{candidate.email}</p>
          </div>
          <div style={{textAlign: 'right'}}>
            <div style={{fontSize: '3rem', fontWeight: 700, color: 'var(--primary-color)', lineHeight: 1}}>
              {candidate.match_score}%
            </div>
            <div style={{color: 'var(--text-light)'}}>Match Score</div>
            <span className={`badge ${candidate.match_score >= 70 ? 'badge-success' : candidate.match_score >= 40 ? 'badge-warning' : 'badge-danger'}`} style={{marginTop: '0.5rem', display: 'inline-block'}}>
              {candidate.recommendation}
            </span>
          </div>
        </div>

        <div className="stats-grid">
          <div style={{background: '#f7fafc', padding: '1.5rem', borderRadius: '8px'}}>
            <h3 style={{display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--success)', marginBottom: '1rem'}}>
              <CheckCircle size={20} /> Matched Skills
            </h3>
            <ul style={{paddingLeft: '1.5rem', lineHeight: 1.6}}>
              {candidate.matching_skills && candidate.matching_skills.length > 0 ? (
                candidate.matching_skills.map((skill, i) => <li key={i}>{skill}</li>)
              ) : (
                <li style={{color: 'var(--text-light)', listStyle: 'none'}}>No exact matches found</li>
              )}
            </ul>
          </div>

          <div style={{background: '#f7fafc', padding: '1.5rem', borderRadius: '8px'}}>
            <h3 style={{display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--danger)', marginBottom: '1rem'}}>
              <XCircle size={20} /> Missing Skills
            </h3>
            <ul style={{paddingLeft: '1.5rem', lineHeight: 1.6}}>
              {candidate.missing_skills && candidate.missing_skills.length > 0 ? (
                candidate.missing_skills.map((skill, i) => <li key={i}>{skill}</li>)
              ) : (
                <li style={{color: 'var(--text-light)', listStyle: 'none'}}>No missing skills</li>
              )}
            </ul>
          </div>
        </div>
        
        <div style={{marginTop: '2rem'}}>
            <h3>Experience</h3>
            <p style={{marginTop: '0.5rem'}}>{candidate.experience}</p>
        </div>
      </div>
    </div>
  );
}
''',
            'About.jsx': '''import React from 'react';

export default function About() {
  return (
    <div className="card">
      <h2 style={{color: 'var(--primary-color)', marginBottom: '1rem'}}>About AI Resume Finder</h2>
      
      <p style={{marginBottom: '1rem', lineHeight: 1.6}}>
        The AI Resume Finder is an intelligent resume screening and job matching system designed to help recruiters 
        quickly identify the best candidates. Instead of manually reading hundreds of resumes, the system uses 
        Natural Language Processing (NLP) and Machine Learning techniques to automate the screening process.
      </p>

      <h3 style={{marginTop: '2rem', marginBottom: '1rem'}}>How it Works (ML Pipeline)</h3>
      <ol style={{paddingLeft: '1.5rem', lineHeight: 1.8}}>
        <li><strong>Text Extraction:</strong> The backend uses <code>pdfplumber</code> and <code>docx2txt</code> to parse text from uploaded files.</li>
        <li><strong>Text Preprocessing:</strong> Text is cleaned, tokenized, and stop words are removed.</li>
        <li><strong>Vectorization:</strong> The job description and resumes are converted into numerical vectors using <strong>TF-IDF</strong> (Term Frequency-Inverse Document Frequency) from <code>scikit-learn</code>.</li>
        <li><strong>Similarity Calculation:</strong> The system calculates the <strong>Cosine Similarity</strong> between the job description vector and each resume vector, generating a match score from 0-100%.</li>
        <li><strong>Information Extraction:</strong> Basic entity extraction identifies matched keywords and missing skills.</li>
      </ol>

      <h3 style={{marginTop: '2rem', marginBottom: '1rem'}}>Technology Stack</h3>
      <ul style={{paddingLeft: '1.5rem', lineHeight: 1.8}}>
        <li><strong>Frontend:</strong> React.js, Vite, Lucide Icons, Vanilla CSS</li>
        <li><strong>Backend:</strong> Python, FastAPI</li>
        <li><strong>Machine Learning:</strong> scikit-learn, NLTK/spaCy</li>
        <li><strong>Database:</strong> MongoDB (Ready for integration)</li>
      </ul>
    </div>
  );
}
'''
        }
    }
}

create_files('backend', backend_files)
create_files('frontend', frontend_files)
print("Scaffolding complete.")
