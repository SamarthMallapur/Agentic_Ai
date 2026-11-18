import { BrowserRouter, NavLink, Route, Routes } from 'react-router-dom'
import { BarChart3, Briefcase, FileCheck2, FileText, Home as HomeIcon, MessageSquare, User } from 'lucide-react'
import { useLoad } from './ui'
import Home from './pages/Home'
import Profile from './pages/Profile'
import Review from './pages/Review'
import Applications from './pages/Applications'
import Interview from './pages/Interview'
import Market from './pages/Market'
import Report from './pages/Report'

const NAV = [
  ['/', 'Home', HomeIcon], ['/profile', 'My Profile', User], ['/applications', 'Applications', Briefcase],
  ['/review', 'Resume Review', FileCheck2], ['/interview', 'Interview Coach', MessageSquare],
  ['/market', 'Market Trends', BarChart3], ['/report', 'Weekly Report', FileText],
]

export default function App() {
  const { data: status } = useLoad('/status')
  return (
    <BrowserRouter>
      <div className="shell">
        <aside className="sidebar">
          <div className="brand">Placement Readiness<span>Companion</span></div>
          <nav>
            {NAV.map(([to, label, Icon]) => (
              <NavLink key={to} to={to} end={to === '/'}><Icon size={17} aria-hidden="true" /><span>{label}</span></NavLink>
            ))}
          </nav>
          {status && <div className="side-status">AI wording: <strong>{status.ai_enabled ? 'On' : 'Off'}</strong><br />Postings: <strong>{status.dataset.postings}</strong>{status.dataset.is_demo ? ' (demo)' : ''}</div>}
        </aside>
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/applications" element={<Applications statuses={status?.statuses || []} />} />
            <Route path="/review" element={<Review />} />
            <Route path="/interview" element={<Interview />} />
            <Route path="/market" element={<Market />} />
            <Route path="/report" element={<Report />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
