import { BrowserRouter, NavLink, Route, Routes, useLocation } from 'react-router-dom'
import { BarChart3, Briefcase, Compass as CompassIcon, FileCheck2, FileText, GraduationCap, Home as HomeIcon, MessageSquare, User } from 'lucide-react'
import { Toaster, useLoad } from './ui'
import Home from './pages/Home'
import Profile from './pages/Profile'
import Review from './pages/Review'
import Applications from './pages/Applications'
import Interview from './pages/Interview'
import Market from './pages/Market'
import Compass from './pages/Compass'
import Report from './pages/Report'

const NAV = [
  ['/', 'Home', HomeIcon], ['/profile', 'My Profile', User], ['/applications', 'Applications', Briefcase],
  ['/review', 'Resume Review', FileCheck2], ['/interview', 'Interview Coach', MessageSquare],
  ['/compass', 'Career Compass', CompassIcon], ['/market', 'Market Trends', BarChart3], ['/report', 'Weekly Report', FileText],
]

function Shell() {
  const { data: status } = useLoad('/status')
  const location = useLocation()
  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand"><span className="logo"><GraduationCap size={20} aria-hidden="true" /></span><span>Placement Readiness<small>Companion</small></span></div>
        <nav>
          {NAV.map(([to, label, Icon]) => (
            <NavLink key={to} to={to} end={to === '/'}><Icon size={17} aria-hidden="true" /><span>{label}</span></NavLink>
          ))}
        </nav>
        {status && <div className="side-status"><span className={`pulse ${status.ai_enabled ? '' : 'off'}`} />AI wording: <strong>{status.ai_enabled ? 'On' : 'Off'}</strong><br />Postings: <strong>{status.dataset.postings}</strong>{status.dataset.is_demo ? ' (demo)' : ''}</div>}
      </aside>
      <main>
        <div className="page" key={location.pathname}>
          <Routes location={location}>
            <Route path="/" element={<Home />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/applications" element={<Applications statuses={status?.statuses || []} />} />
            <Route path="/review" element={<Review />} />
            <Route path="/interview" element={<Interview />} />
            <Route path="/compass" element={<Compass />} />
            <Route path="/market" element={<Market />} />
            <Route path="/report" element={<Report />} />
          </Routes>
        </div>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="aurora" aria-hidden="true"><i /><i /><i /></div>
      <Shell />
      <Toaster />
    </BrowserRouter>
  )
}
