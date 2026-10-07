import React from 'react';

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
