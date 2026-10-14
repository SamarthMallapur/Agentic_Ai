import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { LayoutDashboard, User, FileText, Briefcase, MessageSquare, TrendingUp, BarChart2, Settings } from 'lucide-react';

import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import ResumeAnalyzer from './pages/ResumeAnalyzer';
import Applications from './pages/Applications';
import InterviewCoach from './pages/InterviewCoach';
import MarketTrends from './pages/MarketTrends';
import WeeklyReport from './pages/WeeklyReport';

function Sidebar() {
  const navItems = [
    { path: '/', label: 'Dashboard', icon: <LayoutDashboard /> },
    { path: '/profile', label: 'My Profile', icon: <User /> },
    { path: '/resume', label: 'Resume Analyzer', icon: <FileText /> },
    { path: '/applications', label: 'Applications', icon: <Briefcase /> },
    { path: '/interview', label: 'Interview Coach', icon: <MessageSquare /> },
    { path: '/market', label: 'Market Trends', icon: <TrendingUp /> },
    { path: '/report', label: 'Weekly Report', icon: <BarChart2 /> },
    { path: '/settings', label: 'Settings', icon: <Settings /> },
  ];

  return (
    <div className="sidebar">
      <h2>AURA Companion</h2>
      <nav>
        {navItems.map((item) => (
          <NavLink 
            key={item.path} 
            to={item.path} 
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            {item.icon}
            {item.label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/resume" element={<ResumeAnalyzer />} />
            <Route path="/applications" element={<Applications />} />
            <Route path="/interview" element={<InterviewCoach />} />
            <Route path="/market" element={<MarketTrends />} />
            <Route path="/report" element={<WeeklyReport />} />
            <Route path="/settings" element={<div className="glass-panel"><h1>Settings</h1><p>Configure API Keys here.</p></div>} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
