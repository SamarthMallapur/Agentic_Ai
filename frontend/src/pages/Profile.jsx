import { useState, useEffect } from 'react';
import axios from 'axios';

export default function Profile() {
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:8000/api/profile')
      .then(res => setProfile(res.data))
      .catch(err => console.error(err));
  }, []);

  if (!profile) return <div className="glass-panel stagger-1" style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>Loading Profile...</div>;

  return (
    <div>
      <div className="stagger-1">
        <h1>My Profile</h1>
        <p>Your background and career objectives.</p>
      </div>
      <div className="grid grid-cols-2" style={{ marginTop: '2rem' }}>
        <div className="glass-panel stagger-1">
          <h3 style={{ color: 'var(--accent-primary)', marginBottom: '1.25rem' }}>Basic Information</h3>
          <p><strong>Name:</strong> {profile.name}</p>
          <p><strong>Education:</strong> {profile.education}</p>
          <p><strong>CGPA:</strong> {profile.cgpa}</p>
          <p><strong>Graduation Year:</strong> {profile.graduation_year}</p>
        </div>
        <div className="glass-panel stagger-2">
          <h3 style={{ color: 'var(--accent-secondary)', marginBottom: '1.25rem' }}>Career Goals</h3>
          <p>{profile.career_goals}</p>
          <h3 style={{ marginTop: '1.5rem', color: 'var(--accent-secondary)', marginBottom: '1rem' }}>Target Roles</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {profile.target_roles?.map(r => (
              <span key={r} className="badge badge-primary">{r}</span>
            ))}
          </div>
        </div>
        <div className="glass-panel stagger-3">
          <h3 style={{ color: 'var(--success)', marginBottom: '1.25rem' }}>Technical Skills</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {profile.technical_skills?.map(s => (
              <span key={s} className="badge badge-success">{s}</span>
            ))}
          </div>
        </div>
        <div className="glass-panel stagger-4">
          <h3 style={{ color: 'var(--danger)', marginBottom: '1.25rem' }}>Weak Areas</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {profile.weak_areas?.map(s => (
              <span key={s} className="badge badge-danger">{s}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
