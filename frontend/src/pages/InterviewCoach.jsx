import { useState, useEffect } from 'react';
import axios from 'axios';
import { Play } from 'lucide-react';

export default function InterviewCoach() {
  const [apps, setApps] = useState([]);
  const [selectedApp, setSelectedApp] = useState('');
  const [questions, setQuestions] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    axios.get('http://localhost:8000/api/applications')
      .then(res => setApps(res.data))
      .catch(err => console.error(err));
  }, []);

  const handleGenerate = async () => {
    if (!selectedApp) return;
    setLoading(true);
    const app = apps.find(a => a.id.toString() === selectedApp);
    
    try {
      const res = await axios.post('http://localhost:8000/api/interview/generate', {
        job_description: app.job_description,
        missing_skills: ["System Design", "Docker"] // Mock missing skills for now
      });
      setQuestions(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Interview Coach</h1>
      <p>Generate tailored mock interview questions based on your profile and application.</p>
      
      <div className="glass-panel" style={{ marginBottom: '2rem' }}>
        <div className="form-group" style={{ maxWidth: '400px' }}>
          <label>Select Application</label>
          <select 
            className="form-control" 
            value={selectedApp} 
            onChange={e => setSelectedApp(e.target.value)}
          >
            <option value="">-- Select --</option>
            {apps.map(a => (
              <option key={a.id} value={a.id}>{a.company} - {a.role}</option>
            ))}
          </select>
        </div>
        <button className="btn" onClick={handleGenerate} disabled={loading || !selectedApp}>
          <Play size={18} /> {loading ? 'Generating...' : 'Start Mock Interview'}
        </button>
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
