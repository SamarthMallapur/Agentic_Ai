import { useState } from 'react';
import axios from 'axios';
import { Upload } from 'lucide-react';

export default function ResumeAnalyzer() {
  const [jd, setJd] = useState('');
  const [resumeText, setResumeText] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!jd || (!resumeText && !file)) {
      setError('Please provide a Job Description and either Resume Text or a PDF file.');
      return;
    }
    setError('');
    setLoading(true);

    const formData = new FormData();
    formData.append('jd', jd);
    if (file) {
      formData.append('file', file);
    } else {
      formData.append('resume_text', resumeText);
    }

    try {
      const res = await axios.post('http://localhost:8000/api/resume/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="stagger-1">
        <h1>Resume Analyzer</h1>
        <p>Score your resume against a target job description.</p>
      </div>

      <div className="grid grid-cols-2" style={{ marginTop: '2rem' }}>
        <div className="glass-panel stagger-2">
          <div className="form-group">
            <label>Job Description</label>
            <textarea 
              className="form-control" 
              value={jd} 
              onChange={e => setJd(e.target.value)} 
              placeholder="Paste JD here..."
            />
          </div>
          
          <div className="form-group">
            <label>Upload Resume PDF</label>
            <input 
              type="file" 
              accept=".pdf" 
              onChange={e => setFile(e.target.files[0])} 
              style={{ marginBottom: '1rem', display: 'block', color: 'var(--text-secondary)' }}
            />
          </div>

          <div className="form-group">
            <label>Or Paste Resume Text</label>
            <textarea 
              className="form-control" 
              value={resumeText} 
              onChange={e => setResumeText(e.target.value)} 
              placeholder="Paste Resume text here..."
            />
          </div>

          <button className="btn" onClick={handleAnalyze} disabled={loading} style={{ width: '100%' }}>
            <Upload size={20} /> {loading ? 'Analyzing...' : 'Analyze Resume'}
          </button>
          
          {error && <p style={{ color: 'var(--danger)', marginTop: '1.5rem', textAlign: 'center' }}>{error}</p>}
        </div>

        {result && (
          <div className="glass-panel stagger-3">
            <h2 style={{ fontSize: '2rem', marginBottom: '1.5rem' }}>Results: <span style={{ color: 'var(--success)' }}>{result.score.total_score}</span> / 100</h2>
            
            <div>
              <h3 style={{ color: 'var(--accent-hover)' }}>Missing High-Priority Keywords</h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '2rem' }}>
                {result.gaps.missing_keywords.length > 0 
                  ? result.gaps.missing_keywords.map(kw => <span key={kw} className="badge badge-warning">{kw}</span>)
                  : <span className="badge badge-success">None detected!</span>
                }
              </div>

              <h3 style={{ color: 'var(--accent-hover)' }}>Recommendations</h3>
              <ul style={{ paddingLeft: '1.5rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {result.score.recommendations.map((rec, i) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>
              
              <div style={{ marginTop: '2.5rem', padding: '1.25rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '12px', borderLeft: '4px solid var(--danger)' }}>
                <p style={{ color: 'var(--text-primary)', margin: 0, fontSize: '0.95rem' }}>
                  <strong>Important:</strong> Only add keywords if you have real experience with them.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
