import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload as UploadIcon, File, XCircle, CheckCircle, AlertCircle } from 'lucide-react';
import { useAuth } from '../AuthContext';

export default function Upload({ addToast }) {
  const [files, setFiles] = useState([]);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();
  const { token } = useAuth();

  const validateFiles = (newFiles) => {
    setErrorMsg('');
    setSuccessMsg('');
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
    const validFiles = [];
    
    for (let f of newFiles) {
      if (!allowedTypes.includes(f.type) && !f.name.match(/\.(pdf|docx|doc)$/i)) {
        if (addToast) addToast(`Invalid file type: ${f.name}. Only PDF and DOCX are allowed.`, 'error');
        setErrorMsg(`Invalid file type: ${f.name}. Only PDF and DOCX are allowed.`);
        return [];
      }
      if (f.size > 5 * 1024 * 1024) {
        if (addToast) addToast(`File too large: ${f.name}. Maximum size is 5MB.`, 'error');
        setErrorMsg(`File too large: ${f.name}. Maximum size is 5MB.`);
        return [];
      }
      validFiles.push(f);
    }
    return validFiles;
  };

  const handleFileChange = (e) => {
    const validFiles = validateFiles(Array.from(e.target.files));
    if (validFiles.length > 0) {
      setFiles([...files, ...validFiles]);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const validFiles = validateFiles(Array.from(e.dataTransfer.files));
    if (validFiles.length > 0) {
      setFiles([...files, ...validFiles]);
    }
  };

  const removeFile = (index) => {
    const newFiles = [...files];
    newFiles.splice(index, 1);
    setFiles(newFiles);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (files.length === 0) {
      if (addToast) addToast('Please select at least one resume to upload.', 'error');
      setErrorMsg('Please select at least one resume to upload.');
      return;
    }

    setIsLoading(true);
    setErrorMsg('');
    setSuccessMsg('');

    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('http://localhost:8000/api/resumes/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Upload failed');
      }

      if (data.status === 'success') {
        if (addToast) addToast(data.message, 'success');
        setSuccessMsg(data.message);
        setFiles([]);
      }
    } catch (error) {
      console.error('Error:', error);
      if (addToast) addToast(error.message || 'Failed to connect to backend API', 'error');
      setErrorMsg(error.message || 'Failed to connect to backend API');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 style={{marginBottom: '1.5rem', color: 'var(--primary-color)'}}>Step 1: Upload Candidate Resumes</h2>
      
      {errorMsg && !addToast && (
        <div style={{background: '#fed7d7', color: '#742a2a', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
          <AlertCircle size={20}/> {errorMsg}
        </div>
      )}

      {successMsg && (
        <div style={{background: '#c6f6d5', color: '#22543d', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <CheckCircle size={20}/> {successMsg}
          </div>
          <button onClick={() => navigate('/jd')} className="btn btn-primary" style={{padding: '0.5rem 1rem'}}>
            Next: Enter Job Description
          </button>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Upload Resumes (Max 5MB per file)</label>
          <div 
            className="file-upload" 
            style={{ borderColor: isDragging ? 'var(--primary-color)' : '#cbd5e0', backgroundColor: isDragging ? 'rgba(15, 76, 129, 0.05)' : 'transparent' }}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current.click()}
          >
            <UploadIcon size={32} color={isDragging ? 'var(--primary-color)' : 'var(--text-light)'} style={{marginBottom: '0.5rem'}} />
            <p style={{fontWeight: 500, color: 'var(--text-dark)'}}>Drag & drop PDF/DOCX files here</p>
            <p style={{fontSize: '0.85rem', color: 'var(--text-light)', marginTop: '0.25rem'}}>or click to browse from your computer</p>
            <input 
              ref={fileInputRef}
              type="file" 
              multiple 
              accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              style={{display: 'none'}}
              onChange={handleFileChange}
            />
          </div>
          
          {files.length > 0 && (
            <div style={{marginTop: '1.5rem'}}>
              <p style={{fontWeight: 600, marginBottom: '0.5rem'}}>Files to Process ({files.length}):</p>
              <ul style={{listStyle: 'none', display: 'grid', gap: '0.5rem'}}>
                {files.map((f, i) => (
                  <li key={i} style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem', background: '#f7fafc', borderRadius: '6px', border: '1px solid #e2e8f0'}}>
                    <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem', overflow: 'hidden'}}>
                      <File size={18} color="var(--primary-color)" /> 
                      <span style={{whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden'}}>{f.name}</span>
                      <span style={{color: 'var(--text-light)', fontSize: '0.85rem'}}>({(f.size / 1024 / 1024).toFixed(2)} MB)</span>
                    </div>
                    <button type="button" onClick={() => removeFile(i)} style={{background: 'none', border: 'none', color: 'var(--text-light)', cursor: 'pointer'}}>
                      <XCircle size={18} />
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <button type="submit" className="btn btn-primary" disabled={isLoading || files.length === 0} style={{width: '100%', fontSize: '1.1rem', marginTop: '1rem'}}>
          {isLoading ? 'Uploading & Parsing...' : 'Upload Resumes'}
        </button>
      </form>
    </div>
  );
}
