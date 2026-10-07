import React, { useState } from 'react';
import { useAuth } from '../AuthContext';
import { Link } from 'react-router-dom';
import { Lock, User } from 'lucide-react';

export default function Login({ addToast }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      addToast('Please fill in all fields', 'error');
      return;
    }

    setLoading(true);
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const res = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });

      const data = await res.json();
      if (res.ok) {
        addToast('Login successful', 'success');
        login(data.access_token);
      } else {
        addToast(data.detail || 'Login failed', 'error');
      }
    } catch (err) {
      addToast('Server error. Please try again later.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{maxWidth: '400px', margin: '4rem auto', padding: '2rem', background: '#fff', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)'}}>
      <h2 style={{textAlign: 'center', marginBottom: '2rem', color: 'var(--primary-color)'}}>Welcome Back</h2>
      <form onSubmit={handleLogin} style={{display: 'flex', flexDirection: 'column', gap: '1.5rem'}}>
        <div>
          <label style={{display: 'block', marginBottom: '0.5rem', fontWeight: 600}}>Username</label>
          <div style={{position: 'relative'}}>
            <User size={18} style={{position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: '#a0aec0'}}/>
            <input 
              type="text" 
              value={username} 
              onChange={e => setUsername(e.target.value)}
              style={{width: '100%', padding: '0.75rem 1rem 0.75rem 2.5rem', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '1rem'}}
              placeholder="Enter your username"
            />
          </div>
        </div>
        <div>
          <label style={{display: 'block', marginBottom: '0.5rem', fontWeight: 600}}>Password</label>
          <div style={{position: 'relative'}}>
            <Lock size={18} style={{position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: '#a0aec0'}}/>
            <input 
              type="password" 
              value={password} 
              onChange={e => setPassword(e.target.value)}
              style={{width: '100%', padding: '0.75rem 1rem 0.75rem 2.5rem', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '1rem'}}
              placeholder="Enter your password"
            />
          </div>
        </div>
        <button 
          type="submit" 
          disabled={loading}
          style={{padding: '0.75rem', background: 'var(--primary-color)', color: '#fff', border: 'none', borderRadius: '8px', fontSize: '1.1rem', cursor: loading ? 'not-allowed' : 'pointer', fontWeight: 600}}
        >
          {loading ? 'Logging in...' : 'Log In'}
        </button>
      </form>
      <p style={{textAlign: 'center', marginTop: '1.5rem', color: 'var(--text-light)'}}>
        Don't have an account? <Link to="/register" style={{color: 'var(--primary-color)', fontWeight: 600, textDecoration: 'none'}}>Register here</Link>
      </p>
    </div>
  );
}
