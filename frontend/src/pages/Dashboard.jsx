import { useState, useEffect } from 'react';
import axios from 'axios';
import { Target, Briefcase, Users, Award } from 'lucide-react';

export default function Dashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:8000/api/dashboard')
      .then(res => setData(res.data))
      .catch(err => console.error(err));
  }, []);

  if (!data) return <div className="glass-panel stagger-1" style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>Loading Dashboard...</div>;

  return (
    <div>
      <div className="stagger-1">
        <h1>Welcome back!</h1>
        <p>Here is your placement readiness overview for this week.</p>
      </div>
      
      <div className="grid grid-cols-4" style={{ marginTop: '2.5rem' }}>
        <div className="glass-panel metric-card stagger-1">
          <Target size={36} color="var(--accent-primary)" style={{ marginBottom: '1rem' }} />
          <h3>Readiness Score</h3>
          <p className="value">{data.readiness_score}</p>
        </div>
        <div className="glass-panel metric-card stagger-2">
          <Briefcase size={36} color="var(--warning)" style={{ marginBottom: '1rem' }} />
          <h3>Applications</h3>
          <p className="value">{data.total_applications}</p>
        </div>
        <div className="glass-panel metric-card stagger-3">
          <Users size={36} color="var(--accent-secondary)" style={{ marginBottom: '1rem' }} />
          <h3>Interviews</h3>
          <p className="value">{data.interviews}</p>
        </div>
        <div className="glass-panel metric-card stagger-4">
          <Award size={36} color="var(--success)" style={{ marginBottom: '1rem' }} />
          <h3>Offers</h3>
          <p className="value">{data.offers}</p>
        </div>
      </div>
    </div>
  );
}
