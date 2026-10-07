import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate, useLocation } from 'react-router-dom';
import Home from './pages/Home';
import Upload from './pages/Upload';
import JobDescription from './pages/JobDescription';
import Dashboard from './pages/Dashboard';
import Details from './pages/Details';
import About from './pages/About';
import MLAnalysis from './pages/MLAnalysis';
import Login from './pages/Login';
import Register from './pages/Register';
import { AuthProvider, useAuth } from './AuthContext';
import { Search, UploadCloud, LayoutDashboard, Info, FileText, Activity, LogIn, LogOut, UserPlus } from 'lucide-react';
import './App.css';

// Toast Component
function Toast({ message, type, onClose }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  const bg = type === 'error' ? '#fed7d7' : '#c6f6d5';
  const color = type === 'error' ? '#9b2c2c' : '#22543d';

  return (
    <div style={{
      position: 'fixed', top: '20px', right: '20px', background: bg, color: color,
      padding: '1rem 1.5rem', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      zIndex: 1000, fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem',
      animation: 'slideIn 0.3s ease-out'
    }}>
      {message}
    </div>
  );
}

// Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  const location = useLocation();
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />;
  return children;
};

function AppContent() {
  const [candidates, setCandidates] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [toast, setToast] = useState(null);
  const { user, logout } = useAuth();

  const addToast = (message, type = 'success') => setToast({ message, type });

  return (
    <div className="app-container">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}
      <nav className="navbar">
        <Link to="/" className="navbar-brand">
          <Search size={24} />
          AI Resume Finder
        </Link>
        <div className="nav-links">
          <Link to="/"><LayoutDashboard size={18}/> Home</Link>
          {user ? (
            <>
              <Link to="/upload"><UploadCloud size={18}/> Upload</Link>
              <Link to="/jd"><FileText size={18}/> Jobs</Link>
              <Link to="/dashboard"><LayoutDashboard size={18}/> Dashboard</Link>
              <Link to="/ml-analysis"><Activity size={18}/> Analysis</Link>
              <button onClick={logout} style={{background: 'none', border: 'none', color: '#e2e8f0', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1rem', fontWeight: 500}}>
                <LogOut size={18}/> Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login"><LogIn size={18}/> Login</Link>
              <Link to="/register"><UserPlus size={18}/> Register</Link>
            </>
          )}
          <Link to="/about"><Info size={18}/> About</Link>
        </div>
      </nav>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login addToast={addToast} />} />
          <Route path="/register" element={<Register addToast={addToast} />} />
          <Route path="/about" element={<About />} />
          
          <Route path="/upload" element={<ProtectedRoute><Upload addToast={addToast} /></ProtectedRoute>} />
          <Route path="/jd" element={<ProtectedRoute><JobDescription setCandidates={setCandidates} setIsLoading={setIsLoading} isLoading={isLoading} addToast={addToast} /></ProtectedRoute>} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard candidates={candidates} isLoading={isLoading} addToast={addToast} /></ProtectedRoute>} />
          <Route path="/candidate/:id" element={<ProtectedRoute><Details candidates={candidates} addToast={addToast} /></ProtectedRoute>} />
          <Route path="/ml-analysis" element={<ProtectedRoute><MLAnalysis addToast={addToast} /></ProtectedRoute>} />
        </Routes>
      </main>

      <footer className="footer">
        <p>&copy; {new Date().getFullYear()} AI Resume Finder. ML-Powered Job Matching System.</p>
      </footer>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;
