import { useState, useEffect } from 'react';
import axios from 'axios';

export default function Applications() {
  const [apps, setApps] = useState([]);
  
  useEffect(() => {
    fetchApps();
  }, []);

  const fetchApps = () => {
    axios.get('http://localhost:8000/api/applications')
      .then(res => setApps(res.data))
      .catch(err => console.error(err));
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'OFFER': return 'badge-success';
      case 'REJECTED': return 'badge-danger';
      case 'INTERVIEW': 
      case 'TECHNICAL_INTERVIEW': return 'badge-primary';
      default: return 'badge-warning';
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h1>Application Tracker</h1>
        <button className="btn">Add Application</button>
      </div>
      
      <div className="glass-panel table-container">
        <table>
          <thead>
            <tr>
              <th>Company</th>
              <th>Role</th>
              <th>Date Applied</th>
              <th>Status</th>
              <th>Resume Score</th>
            </tr>
          </thead>
          <tbody>
            {apps.map(app => (
              <tr key={app.id}>
                <td><strong>{app.company}</strong></td>
                <td>{app.role}</td>
                <td>{app.application_date || '-'}</td>
                <td><span className={`badge ${getStatusColor(app.status)}`}>{app.status.replace('_', ' ')}</span></td>
                <td>{app.resume_score ? `${app.resume_score}/100` : '-'}</td>
              </tr>
            ))}
            {apps.length === 0 && (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>No applications found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
