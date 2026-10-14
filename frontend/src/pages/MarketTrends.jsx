import { useState, useEffect } from 'react';
import axios from 'axios';

export default function MarketTrends() {
  const [trends, setTrends] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:8000/api/market')
      .then(res => setTrends(res.data))
      .catch(err => console.error(err));
  }, []);

  if (!trends) return <div className="glass-panel">Loading...</div>;

  return (
    <div>
      <h1>Market Trends</h1>
      <p>Analysis of {trends.total_jobs_analyzed} local job postings.</p>

      <div className="grid grid-cols-2">
        <div className="glass-panel">
          <h3 style={{ color: 'var(--accent-primary)' }}>Top Skills in Demand</h3>
          <div style={{ marginTop: '1rem' }}>
            {trends.top_skills.map((skill, i) => {
              const pct = trends.skill_demand_percentage[skill[0]];
              return (
                <div key={skill[0]} style={{ marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                    <span>{i + 1}. {skill[0]}</span>
                    <span style={{ color: 'var(--text-secondary)' }}>{pct}%</span>
                  </div>
                  <div style={{ width: '100%', background: 'rgba(255,255,255,0.1)', height: '8px', borderRadius: '4px' }}>
                    <div style={{ width: `${pct}%`, background: 'var(--accent-hover)', height: '100%', borderRadius: '4px' }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="glass-panel">
          <h3 style={{ color: 'var(--accent-primary)' }}>Common Roles</h3>
          <ul style={{ paddingLeft: '1.5rem', marginTop: '1rem', color: 'var(--text-secondary)' }}>
            {trends.common_roles.map(role => (
              <li key={role[0]} style={{ marginBottom: '0.5rem' }}>
                <strong style={{ color: 'var(--text-primary)' }}>{role[0]}</strong> ({role[1]} postings)
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
