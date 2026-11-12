import { useState } from 'react'
import { Activity, ChartNoAxesCombined, MessagesSquare, Route, Menu, X, ShieldCheck } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Copilot from './pages/Copilot'

const pages = [
  { id: 'dashboard', label: 'Intelligence dashboard', icon: ChartNoAxesCombined },
  { id: 'copilot', label: 'AI product copilot', icon: MessagesSquare }
]

export default function App() {
  const [page, setPage] = useState('dashboard')
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileOpen ? 'mobile-open' : ''}`}>
        <div className="brand">
          <div className="brand-mark"><Route size={25} strokeWidth={2.5} /></div>
          <div><div className="brand-name">zipro<span>.</span></div><div className="brand-subtitle">Voice of Customer Copilot</div></div>
          <button className="mobile-close icon-btn" onClick={() => setMobileOpen(false)} aria-label="Close menu"><X size={19}/></button>
        </div>
        <div className="nav-caption">WORKSPACE</div>
        <nav className="nav-list">
          {pages.map(({ id, label, icon: Icon }) => (
            <button key={id} className={`nav-item ${page === id ? 'active' : ''}`} onClick={() => { setPage(id); setMobileOpen(false) }}>
              <Icon size={19}/><span>{label}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-info"><ShieldCheck size={18}/><span>Evidence-first intelligence</span></div>
          <div className="sidebar-note">Independent synthetic case study<br/>Not affiliated with a real operator</div>
        </div>
      </aside>
      <main className="main-content">
        <header className="topbar">
          <button className="mobile-menu icon-btn" onClick={() => setMobileOpen(true)} aria-label="Open menu"><Menu size={22}/></button>
          <div className="breadcrumb">Workspace <span>/</span> <strong>{page === 'dashboard' ? 'Customer intelligence' : 'AI product copilot'}</strong></div>
        </header>
        <div className="page-container">
          <div style={{display: page === 'dashboard' ? 'block' : 'none'}}><Dashboard openCopilot={() => setPage('copilot')}/></div>
          <div style={{display: page === 'copilot' ? 'block' : 'none'}}><Copilot /></div>
        </div>
      </main>
    </div>
  )
}
