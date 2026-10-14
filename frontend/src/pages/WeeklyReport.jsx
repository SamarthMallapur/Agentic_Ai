import { useState } from 'react';
import axios from 'axios';
import { BarChart2 } from 'lucide-react';

export default function WeeklyReport() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = () => {
    setLoading(true);
    axios.get('http://localhost:8000/api/report')
      .then(res => setReport(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <div>
          <h1>Weekly Report</h1>
          <p>Comprehensive overview of your readiness status.</p>
        </div>
        <button className="btn" onClick={handleGenerate} disabled={loading}>
          <BarChart2 size={18} /> {loading ? 'Compiling...' : 'Generate Report'}
        </button>
      </div>

      {report && (
        <div className="grid grid-cols-1" style={{ animation: 'fadeIn 0.5s ease' }}>
          
          <div className="glass-panel">
            <h2 style={{ color: 'var(--accent-hover)' }}>Market Demand vs Your Profile</h2>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', marginTop: '1rem' }}>
              {Object.entries(report.market_demand_comparison).map(([skill, hasSkill]) => (
                <div key={skill} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(255,255,255,0.05)', padding: '0.5rem 1rem', borderRadius: '8px' }}>
                  <span style={{ fontSize: '1.2rem' }}>{hasSkill ? '✅' : '❌'}</span>
                  <span>{skill}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-panel">
            <h2 style={{ color: 'var(--warning)' }}>Recommended Actions</h2>
            {report.recommended_actions.map((act, i) => (
              <div key={i} style={{ marginBottom: '1rem', padding: '1rem', background: 'rgba(245, 158, 11, 0.1)', borderLeft: '4px solid var(--warning)', borderRadius: '8px' }}>
                <h3 style={{ margin: 0, color: 'var(--warning)', fontSize: '1.1rem' }}>{act.action}</h3>
                <p style={{ margin: '0.5rem 0', color: 'var(--text-primary)' }}>{act.why}</p>
                <p style={{ margin: 0, fontSize: '0.9rem' }}><strong>Expected Benefit:</strong> {act.expected_benefit}</p>
              </div>
            ))}
            {report.recommended_actions.length === 0 && <p>No specific actions recommended at this time.</p>}
          </div>

          <div className="glass-panel">
            <h2 style={{ color: 'var(--success)' }}>Evidence Table (QA Governed)</h2>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Claim</th>
                    <th>Evidence</th>
                    <th>Source</th>
                    <th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {report.evidence_table.map((ev, i) => (
                    <tr key={i}>
                      <td><strong>{ev.claim}</strong></td>
                      <td>{ev.evidence}</td>
                      <td>{ev.source} (n={ev.sample_size})</td>
                      <td>
                        <span className={`badge ${ev.confidence === 'High' ? 'badge-success' : 'badge-warning'}`}>
                          {ev.confidence}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
