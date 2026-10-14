import { useState, useEffect } from 'react';
import axios from 'axios';
import { Play, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function InterviewCoach() {
  const [apps, setApps] = useState([]);
  const [selectedApp, setSelectedApp] = useState('');
  const [questions, setQuestions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fetchingApps, setFetchingApps] = useState(true);
  const [fetchError, setFetchError] = useState(null);
  const [genError, setGenError] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:8000/api/applications')
      .then(res => {
        setApps(res.data);
        if (res.data && res.data.length > 0) {
          setSelectedApp(res.data[0].id.toString());
        }
      })
      .catch(err => {
        console.error(err);
        setFetchError('Failed to load applications from backend. Ensure API is running on http://localhost:8000.');
      })
      .finally(() => setFetchingApps(false));
  }, []);

  const handleGenerate = async () => {
    if (!selectedApp) return;
    setLoading(true);
    setGenError(null);
    const app = apps.find(a => a.id.toString() === selectedApp);
    
    try {
      const res = await axios.post('http://localhost:8000/api/interview/generate', {
        job_description: app?.job_description || "Software Engineer role requiring coding, algorithms, and system design.",
        missing_skills: ["System Design", "Docker"]
      });
      setQuestions(res.data);
    } catch (err) {
      console.error(err);
      setGenError(err.response?.data?.detail || err.message || 'Failed to generate interview questions.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Interview Coach</h1>
      <p>Generate tailored mock interview questions based on your profile and application.</p>
      
      {fetchError && (
        <div className="glass-panel" style={{ borderLeft: '4px solid var(--danger)', marginBottom: '1.5rem', color: 'var(--danger)' }}>
          <p style={{ margin: 0 }}>{fetchError}</p>
        </div>
      )}

      <div className="glass-panel" style={{ marginBottom: '2rem' }}>
        <div className="form-group" style={{ maxWidth: '400px' }}>
          <label>Select Application</label>
          <select 
            className="form-control" 
            value={selectedApp} 
            onChange={e => setSelectedApp(e.target.value)}
            disabled={fetchingApps || apps.length === 0}
          >
            {apps.length === 0 ? (
              <option value="">{fetchingApps ? 'Loading applications...' : 'No applications available'}</option>
            ) : (
              <>
                <option value="">-- Select an application --</option>
                {apps.map(a => (
                  <option key={a.id} value={a.id}>{a.company} - {a.role}</option>
                ))}
              </>
            )}
          </select>
        </div>

        {apps.length === 0 && !fetchingApps && (
          <div style={{ marginBottom: '1rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertCircle size={16} color="var(--warning)" />
            <span>No job applications found. <Link to="/applications" style={{ color: 'var(--accent-hover)', textDecoration: 'underline' }}>Add an application here</Link> or run seed data.</span>
          </div>
        )}

        <button className="btn" onClick={handleGenerate} disabled={loading || !selectedApp}>
          <Play size={18} /> {loading ? 'Generating Questions...' : 'Start Mock Interview'}
        </button>

        {genError && (
          <p style={{ color: 'var(--danger)', marginTop: '1rem' }}>{genError}</p>
        )}
      </div>

      {questions && (
        <div className="grid grid-cols-2">
          {Array.isArray(questions) ? questions.map((q, i) => (
            <div key={i} className="glass-panel" style={{ animation: 'fadeIn 0.5s ease' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <span className="badge badge-primary">{q.category}</span>
                <span className={`badge ${q.difficulty === 'Hard' ? 'badge-danger' : q.difficulty === 'Medium' ? 'badge-warning' : 'badge-success'}`}>
                  {q.difficulty}
                </span>
              </div>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>{q.question}</h3>
              
              <details style={{ cursor: 'pointer' }}>
                <summary style={{ color: 'var(--accent-hover)', fontWeight: 500, marginBottom: '0.5rem' }}>Show Expected Points</summary>
                <ul style={{ paddingLeft: '1.5rem', color: 'var(--text-secondary)' }}>
                  {q.expected_answer_points?.map((pt, j) => (
                    <li key={j} style={{ marginBottom: '0.25rem' }}>{pt}</li>
                  ))}
                </ul>
              </details>
            </div>
          )) : <div className="glass-panel"><pre style={{ whiteSpace: 'pre-wrap' }}>{questions.raw}</pre></div>}
        </div>
      )}
    </div>
  );
}
